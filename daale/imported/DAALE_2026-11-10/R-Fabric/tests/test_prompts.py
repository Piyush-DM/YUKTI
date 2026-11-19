"""The kernel prompts must tell each model what validation will enforce on its reply."""

import json
import unittest
from pathlib import Path

from daale.pipeline import BASE_KERNELS
from daale.prompts import KERNEL_SYSTEM_PROMPTS, _json, build_adversary_messages, build_kernel_messages
from daale.schemas import CHALLENGE_TYPES, CLAIM_STATUSES, KERNEL_OUTPUT_SCHEMA, REQUIREMENT_STATES

ROOT = Path(__file__).resolve().parents[1]


def load(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class KernelPromptTests(unittest.TestCase):
    def test_every_base_kernel_is_told_where_each_verdict_goes(self):
        # Only four of the six used to say so; the two that did not (CONTRARIAN and
        # OUTSIDER) were the two that failed in the first live run.
        for kernel in BASE_KERNELS:
            prompt = KERNEL_SYSTEM_PROMPTS[kernel]
            with self.subTest(kernel=kernel):
                self.assertIn("goes in its 'status' field (SATISFIED, NOT_SATISFIED, or UNKNOWN)", prompt)
                self.assertIn("goes in its 'relation' field", prompt)

    def test_kernels_that_may_challenge_are_told_what_a_challenge_status_can_be(self):
        for kernel in ("CONTRARIAN", "OUTSIDER"):
            prompt = KERNEL_SYSTEM_PROMPTS[kernel]
            with self.subTest(kernel=kernel):
                for value in CHALLENGE_TYPES:
                    self.assertIn(value, prompt)
                self.assertIn("Never put SATISFIED, NOT_SATISFIED, UNKNOWN", prompt)

    def test_no_base_kernel_is_told_it_may_return_an_empty_findings_array(self):
        # Base kernels must always return the full relation matrix; only the adversary,
        # which produces nothing but challenges, may answer with no findings.
        for kernel in BASE_KERNELS:
            with self.subTest(kernel=kernel):
                self.assertNotIn("empty findings array", KERNEL_SYSTEM_PROMPTS[kernel])
        self.assertIn("empty findings array", KERNEL_SYSTEM_PROMPTS["ADVERSARY"])

    def test_the_outsider_and_contrarian_keep_their_own_roles(self):
        self.assertIn("OUTSIDER kernel", KERNEL_SYSTEM_PROMPTS["OUTSIDER"])
        self.assertIn("a regulator", KERNEL_SYSTEM_PROMPTS["OUTSIDER"])
        self.assertIn("CONTRARIAN kernel", KERNEL_SYSTEM_PROMPTS["CONTRARIAN"])
        self.assertIn("argue against the prevailing consensus", KERNEL_SYSTEM_PROMPTS["CONTRARIAN"])

    def test_every_base_kernel_is_told_how_to_address_a_finding_about_the_whole_case(self):
        # The second live run lost an OUTSIDER attempt to RISK and GAP findings with no
        # target_id: nothing told it what to put there when no single claim was meant.
        for kernel in BASE_KERNELS:
            with self.subTest(kernel=kernel):
                self.assertIn(
                    "target_type 'GENERAL' and target_id 'GENERAL'", KERNEL_SYSTEM_PROMPTS[kernel]
                )

    def test_the_kernels_that_add_findings_are_told_to_keep_them_few_and_short(self):
        # The first live run cut CONTRARIAN off at its token ceiling.
        for kernel in ("CONTRARIAN", "OUTSIDER"):
            prompt = KERNEL_SYSTEM_PROMPTS[kernel]
            with self.subTest(kernel=kernel):
                self.assertIn("no more than six", prompt)
                self.assertIn("one or two sentences", prompt)


class PromptedSchemaTests(unittest.TestCase):
    """The model reads the schema as text, so what the schema says is part of the prompt."""

    @staticmethod
    def properties():
        return KERNEL_OUTPUT_SCHEMA["properties"]["findings"]["items"]["properties"]

    def test_the_schema_says_which_vocabulary_goes_with_which_finding_type(self):
        status = self.properties()["status"]["description"]
        for value in REQUIREMENT_STATES + CLAIM_STATUSES + CHALLENGE_TYPES:
            self.assertIn(value, status)
        for finding_type in ("REQUIREMENT_ASSESSMENT", "CLAIM_ASSESSMENT", "CHALLENGE"):
            self.assertIn(finding_type, status)
        self.assertIn("EVIDENCE_RELATION", self.properties()["relation"]["description"])
        self.assertIn("one or two sentences", self.properties()["content"]["description"])
        self.assertIn("GENERAL", self.properties()["target_id"]["description"])

    def test_those_descriptions_reach_the_model_in_the_prompt(self):
        messages = build_kernel_messages(
            "OUTSIDER",
            load("cases/vendor_alpha.json"),
            load("policies/vendor_post_technical_dd_v0_1.json"),
            None,
            False,
        )
        self.assertIn("Leave it out on every other finding type", messages[1]["content"])

    def test_the_descriptions_change_nothing_about_what_validates(self):
        from jsonschema import Draft202012Validator

        Draft202012Validator.check_schema(KERNEL_OUTPUT_SCHEMA)
        Draft202012Validator(KERNEL_OUTPUT_SCHEMA).validate(load("fixtures/analyst_output.json"))


class EvidenceSeparationTests(unittest.TestCase):
    def setUp(self):
        self.case = load("cases/vendor_alpha.json")
        self.policy = load("policies/vendor_post_technical_dd_v0_1.json")

    def test_disabled_mode_keeps_the_existing_prompt_layout(self):
        default = build_kernel_messages("ANALYST", self.case, self.policy, None, False)
        explicit_off = build_kernel_messages(
            "ANALYST", self.case, self.policy, None, False, isolate_evidence=False
        )
        self.assertEqual(default, explicit_off)
        self.assertTrue(default[1]["content"].startswith(f"CASE:\n{_json(self.case)}\n\n"))

    def test_enabled_mode_preserves_evidence_and_repeats_task_after_boundary(self):
        messages = build_kernel_messages(
            "ANALYST", self.case, self.policy, None, False, isolate_evidence=True
        )
        user = messages[1]["content"]
        start = user.index("<<<YUKTI_EVIDENCE_")
        line_end = user.index("\n", start)
        token = user[start:line_end]
        end = user.index(token, line_end + 1)
        evidence_text = user[line_end + 1:end].strip()
        self.assertEqual(json.loads(evidence_text), self.case["evidence"])
        self.assertIn("UNTRUSTED EVIDENCE DATA BLOCK", user)
        task_marker = "AUTHORITATIVE TASK INSTRUCTIONS (repeated after the evidence block):"
        self.assertGreater(user.index(task_marker), end)
        self.assertIn(messages[0]["content"], user[user.index(task_marker):])

    def test_boundary_is_deterministic_and_changes_with_case_content(self):
        first = build_kernel_messages(
            "ANALYST", self.case, self.policy, None, False, isolate_evidence=True
        )[1]["content"]
        repeated = build_kernel_messages(
            "ANALYST", self.case, self.policy, None, False, isolate_evidence=True
        )[1]["content"]
        changed_case = json.loads(json.dumps(self.case))
        changed_case["evidence"][0]["text"] += " amended"
        changed = build_kernel_messages(
            "ANALYST", changed_case, self.policy, None, False, isolate_evidence=True
        )[1]["content"]
        self.assertEqual(first, repeated)
        first_token = first[first.index("<<<YUKTI_EVIDENCE_"):].splitlines()[0]
        changed_token = changed[changed.index("<<<YUKTI_EVIDENCE_"):].splitlines()[0]
        self.assertNotEqual(first_token, changed_token)

    def test_adversary_uses_the_same_opt_in_evidence_boundary(self):
        messages = build_adversary_messages(
            self.case, self.policy, {"analyst": {"findings": []}}, False,
            isolate_evidence=True,
        )
        user = messages[1]["content"]
        self.assertIn("UNTRUSTED EVIDENCE DATA BLOCK", user)
        self.assertIn("PRIOR KERNEL OUTPUTS:", user)
        task_marker = "AUTHORITATIVE TASK INSTRUCTIONS (repeated after the evidence block):"
        self.assertGreater(user.index(task_marker), user.index("<<<YUKTI_EVIDENCE_"))


if __name__ == "__main__":
    unittest.main()
