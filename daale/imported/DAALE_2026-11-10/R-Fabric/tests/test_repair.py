"""A rejected reply is shown to the model on retry, whichever check rejected it.

The 2026-11-09 live run lost OUTSIDER twice to the same mistake: two findings with no target_id.
The schema check sits inside the client, which raised an error that carried no reply, so the retry
was blind and, at temperature 0, repeated the mistake exactly.
"""

import json
import unittest
from unittest import mock

from daale.client import CompletionRecord, DaaleModelError, GenericApiClient
from daale.pipeline import DaalePipeline, _repair_instruction
from daale.schemas import KERNEL_OUTPUT_SCHEMA
from tests.test_integrity_rules import load


def outsider_without_a_target_id():
    """The OUTSIDER fixture with one RISK finding stripped of its target_id."""
    output = load("fixtures/outsider_output.json")
    findings = output["findings"]
    index = next(i for i, finding in enumerate(findings) if finding["finding_type"] == "RISK")
    finding_id = findings[index]["finding_id"]
    del findings[index]["target_id"]
    return output, index, finding_id


class ClientTests(unittest.TestCase):
    def test_a_reply_that_breaks_the_schema_carries_itself_on_the_error(self):
        output, _, _ = outsider_without_a_target_id()
        reply = mock.Mock(ok=True, status_code=200, headers={}, text="x")
        reply.json.return_value = {
            "id": "r",
            "model": "m",
            "choices": [{"message": {"content": json.dumps(output)}}],
            "usage": {},
        }
        client = GenericApiClient(api_key="k", base_url="https://example.test/v1")
        with mock.patch("daale.client.requests.post", return_value=reply):
            with self.assertRaises(DaaleModelError) as raised:
                client.complete_json(
                    "outsider", "m", [{"role": "user", "content": "x"}], KERNEL_OUTPUT_SCHEMA
                )
        self.assertEqual(raised.exception.output, output)
        self.assertIn("'target_id' is a required property", str(raised.exception))


class SchemaRejectingClient:
    """Answers from the fixtures, except that the first OUTSIDER reply breaks the schema the way
    the real client reports it: an error that carries the rejected reply."""

    def __init__(self):
        self.outsider_messages = []
        self.rejected_output, index, self.finding_id = outsider_without_a_target_id()
        self.message = (
            "outsider model output failed schema validation: "
            f"findings.{index}: 'target_id' is a required property"
        )

    def complete_json(self, purpose, model, messages, schema):
        if purpose == "outsider":
            self.outsider_messages.append(messages)
            if len(self.outsider_messages) == 1:
                error = DaaleModelError(self.message)
                error.output = self.rejected_output
                raise error
        return CompletionRecord(
            purpose=purpose,
            output=load(f"fixtures/{purpose}_output.json"),
            requested_model=model,
            served_model=model,
            request_id=f"req-{purpose}",
            usage={"total_tokens": 10},
        )


class PipelineRepairTests(unittest.TestCase):
    def setUp(self):
        sleeper = mock.patch("daale.pipeline.time.sleep")
        sleeper.start()
        self.addCleanup(sleeper.stop)

    def test_a_schema_rejection_is_sent_back_with_the_finding_named_and_the_fix_stated(self):
        client = SchemaRejectingClient()
        result = DaalePipeline(client=client, model_by_kernel={"default": "m"}).run(
            load("cases/vendor_alpha.json"), load("policies/vendor_post_technical_dd_v0_1.json")
        )
        self.assertEqual(len(client.outsider_messages), 2)
        retry = client.outsider_messages[1]
        self.assertEqual([m["role"] for m in retry], ["system", "user", "assistant", "user"])
        self.assertEqual(json.loads(retry[2]["content"]), client.rejected_output)
        correction = retry[-1]["content"]
        self.assertIn("rejected by validation", correction)
        self.assertIn(f"finding_id {client.finding_id}", correction)
        self.assertIn("target_type 'GENERAL' and target_id 'GENERAL'", correction)
        self.assertEqual(result.decision_packet["execution_integrity"]["base_kernels_failed"], [])


class RepairInstructionTests(unittest.TestCase):
    def test_the_original_error_text_is_kept_and_positions_become_finding_ids(self):
        error = DaaleModelError("x failed schema validation: findings.1: 'target_id' is a required property")
        text = _repair_instruction(error, {"findings": [{"finding_id": "A"}, {"finding_id": "B"}]})
        self.assertIn("failed schema validation", text)
        self.assertIn("findings.1 (finding_id B)", text)
        self.assertIn("How to fix", text)

    def test_an_unrecognised_error_gets_no_invented_hint(self):
        self.assertEqual(_repair_instruction(ValueError("case_id mismatch"), {}), "case_id mismatch")

    def test_a_position_beyond_the_findings_is_left_as_it_was(self):
        error = DaaleModelError("findings.9: 'content' is a required property")
        self.assertEqual(
            _repair_instruction(error, {"findings": [{"finding_id": "A"}]}),
            "findings.9: 'content' is a required property",
        )


if __name__ == "__main__":
    unittest.main()
