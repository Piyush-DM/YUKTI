import json
import tempfile
import unittest
from pathlib import Path

from daale.intake import (
    IntakeError,
    build_case,
    build_case_from_file,
    chunk_spans,
    describe,
    verify_provenance,
)
from daale.validation import validate_case_and_policy

ROOT = Path(__file__).resolve().parents[1]

REPORT = """# Security report

The vendor completed an external penetration test in September. No critical
findings were reported by the testers.

## Compliance

No SOC 2 Type II report has been supplied to us.

The vendor states one is in progress.
"""

NOTES = "Call notes: the account lead said support is available 24 hours a day.\n"


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.base = Path(self._dir.name)
        (self.base / "report.md").write_text(REPORT, encoding="utf-8")
        (self.base / "notes.txt").write_text(NOTES, encoding="utf-8")
        self.manifest = {
            "case_id": "DD-TEST-1",
            "decision_stage": "post_technical_due_diligence_approval",
            "decision_question": "Approve the vendor?",
            "claims": [
                {"claim_id": "C1", "text": "The vendor meets the security baseline."},
                {"claim_id": "C2", "text": "The vendor offers 24-hour support."},
            ],
            "documents": [
                {"path": "report.md", "document_id": "DOC-SEC", "title": "Security report",
                 "document_version": "2.1"},
                {"path": "notes.txt", "source_type": "INTERVIEW"},
            ],
        }

    def build(self, **kwargs):
        return build_case(self.manifest, self.base, **kwargs)

    # -- what the output is ------------------------------------------------

    def test_case_passes_the_engine_validation(self):
        case = self.build(min_chars=0)
        policy = json.loads(
            (ROOT / "policies/vendor_post_technical_dd_v0_1.json").read_text(encoding="utf-8")
        )
        validate_case_and_policy(case, policy)

    def test_every_evidence_text_is_an_exact_substring_of_its_file(self):
        case = self.build(min_chars=0)
        self.assertEqual(verify_provenance(case), [])
        full = (self.base / "report.md").read_text(encoding="utf-8")
        report_items = [e for e in case["evidence"] if e["source"]["source_id"] == "S1"]
        self.assertTrue(report_items)
        for item in report_items:
            self.assertIn(item["text"], full)

    def test_ids_follow_manifest_order(self):
        case = self.build(min_chars=0)
        ids = [e["evidence_id"] for e in case["evidence"]]
        self.assertEqual(ids, [f"E{i}" for i in range(1, len(ids) + 1)])
        self.assertEqual(case["evidence"][-1]["source"]["source_id"], "S2")

    def test_provenance_comes_from_the_material(self):
        case = self.build(min_chars=0)
        first = case["evidence"][0]["source"]
        self.assertEqual(first["document_id"], "DOC-SEC")
        self.assertEqual(first["document_version"], "2.1")
        self.assertEqual(first["extraction_method"], "PARSER")
        self.assertEqual(len(first["content_hash"]), 64)
        self.assertTrue(first["source_uri"].startswith("file:"))

    def test_markdown_section_is_the_nearest_heading(self):
        case = self.build(min_chars=0)
        sections = {e["source"].get("section") for e in case["evidence"]
                    if e["source"]["source_id"] == "S1"}
        self.assertIn("Compliance", sections)

    def test_nothing_is_invented_when_the_material_does_not_say(self):
        case = self.build(min_chars=0)
        notes = [e for e in case["evidence"] if e["source"]["source_id"] == "S2"][0]["source"]
        for absent in ("page", "section", "collected_at"):
            self.assertNotIn(absent, notes)
        self.assertEqual(notes["document_id"], "DOC-2")
        self.assertTrue(notes["document_version"].startswith("sha256:"))
        self.assertEqual(notes["source_type"], "INTERVIEW")

    def test_same_material_gives_the_same_case(self):
        self.assertEqual(self.build(min_chars=0), self.build(min_chars=0))

    # -- chunking ----------------------------------------------------------

    def test_short_paragraphs_are_joined_and_long_ones_are_cut(self):
        text = "Short one.\n\nShort two.\n\n" + ("Sentence number one is here. " * 40)
        spans = chunk_spans(text, min_chars=50, max_chars=300)
        for start, end in spans:
            self.assertLessEqual(end - start, 300)
        self.assertGreater(len(spans), 1)
        self.assertTrue(text[spans[0][0]:spans[0][1]].startswith("Short one."))
        self.assertIn("Short two.", text[spans[0][0]:spans[0][1]])

    def test_chunks_cover_the_text_without_overlap(self):
        spans = chunk_spans(REPORT, min_chars=0, max_chars=1500)
        for (_, previous_end), (next_start, _) in zip(spans, spans[1:]):
            self.assertLessEqual(previous_end, next_start)

    # -- refusals ----------------------------------------------------------

    def test_pdf_is_refused_with_a_reason(self):
        (self.base / "scan.pdf").write_bytes(b"%PDF-1.7 not text")
        self.manifest["documents"].append({"path": "scan.pdf"})
        with self.assertRaisesRegex(IntakeError, "convert PDF"):
            self.build()

    def test_binary_content_is_refused(self):
        (self.base / "weird.txt").write_bytes(b"abc\x00def")
        self.manifest["documents"] = [{"path": "weird.txt"}]
        with self.assertRaisesRegex(IntakeError, "binary"):
            self.build()

    def test_missing_and_empty_files_are_refused(self):
        self.manifest["documents"] = [{"path": "gone.txt"}]
        with self.assertRaisesRegex(IntakeError, "not found"):
            self.build()
        (self.base / "blank.txt").write_text("  \n\n", encoding="utf-8")
        self.manifest["documents"] = [{"path": "blank.txt"}]
        with self.assertRaisesRegex(IntakeError, "empty"):
            self.build()

    def test_path_outside_the_manifest_directory_is_refused(self):
        outside = self.base.parent / "outside_intake_test.txt"
        outside.write_text("x" * 300, encoding="utf-8")
        self.addCleanup(outside.unlink)
        self.manifest["documents"] = [{"path": "../outside_intake_test.txt"}]
        with self.assertRaisesRegex(IntakeError, "escapes"):
            self.build()

    def test_claims_must_come_from_the_user(self):
        del self.manifest["claims"]
        with self.assertRaisesRegex(IntakeError, "missing required"):
            self.build()
        self.manifest["claims"] = []
        with self.assertRaisesRegex(IntakeError, "non-empty"):
            self.build()

    def test_unknown_manifest_fields_are_not_silently_ignored(self):
        self.manifest["summary"] = "x"
        with self.assertRaisesRegex(IntakeError, "unknown field"):
            self.build()

    def test_duplicate_claim_ids_are_refused(self):
        self.manifest["claims"].append({"claim_id": "C1", "text": "again"})
        with self.assertRaisesRegex(IntakeError, "duplicate claim_id"):
            self.build()

    def test_too_much_evidence_is_refused_with_the_cost_explained(self):
        with self.assertRaisesRegex(IntakeError, "relations per kernel"):
            self.build(min_chars=0, max_evidence=2)

    # -- provenance verification ------------------------------------------

    def test_a_changed_file_is_detected(self):
        case = self.build(min_chars=0)
        (self.base / "report.md").write_text(REPORT + "\nAdded later.\n", encoding="utf-8")
        problems = verify_provenance(case)
        self.assertTrue(any("hash mismatch" in p for p in problems), problems)

    def test_a_deleted_file_is_detected(self):
        case = self.build(min_chars=0)
        (self.base / "notes.txt").unlink()
        self.assertTrue(any("missing" in p for p in verify_provenance(case)))

    def test_a_tampered_evidence_text_is_detected(self):
        case = self.build(min_chars=0)
        case["evidence"][0]["text"] = "Something the document never said."
        self.assertTrue(any("not found" in p for p in verify_provenance(case)))

    # -- entry points ------------------------------------------------------

    def test_build_from_manifest_file_resolves_paths_next_to_it(self):
        path = self.base / "manifest.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        case = build_case_from_file(path, min_chars=0)
        self.assertIn("relations required per kernel", describe(case))


if __name__ == "__main__":
    unittest.main()
