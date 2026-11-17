"""The kernel prompts must tell each model what validation will enforce on its reply."""

import json
import unittest
from pathlib import Path

from daale.pipeline import BASE_KERNELS
from daale.prompts import KERNEL_SYSTEM_PROMPTS, build_kernel_messages
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


if __name__ == "__main__":
    unittest.main()
