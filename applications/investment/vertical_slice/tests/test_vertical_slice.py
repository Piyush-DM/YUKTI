"""The vertical slice runs end to end, inspectably and deterministically.

The load-bearing test here is ``test_parsing_introduces_no_semantics``. The
slice's whole claim is that it added a document intake layer and changed nothing
else, and the only way to hold that claim honestly is to check that the packet
parsed from the document is equal to the packet frozen inside the prototype. If
intake ever starts interpreting, defaulting, or normalising, that test fails --
and it fails before any downstream result has a chance to look plausible.

Tests write into a temporary directory rather than ``reports/``, so running the
suite does not leave artifacts behind or overwrite a run someone is reading.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from choir_prototype.core.pipeline import execute
from choir_prototype.core.replay import verify
from choir_prototype.domains import investment
from choir_prototype.domains.investment.packets import ORBITAL_SERIES_B

from applications.investment.vertical_slice import run as slice_run
from applications.investment.vertical_slice.parse import (
    DOCUMENT_VERSION,
    SAMPLE_DOCUMENT,
    load_sample_packet,
    parse_document,
    read_document,
)


class TestDocumentIntake(unittest.TestCase):
    """The parsing layer maps shapes and does nothing else."""

    def test_sample_document_exists(self) -> None:
        """The slice runs a fixed document committed alongside it."""
        self.assertTrue(SAMPLE_DOCUMENT.is_file())

    def test_parsing_introduces_no_semantics(self) -> None:
        """The parsed packet equals the packet frozen in the prototype.

        This is the guard on the slice's central claim: intake is a shape
        mapping, not a reinterpretation of the case material.
        """
        self.assertEqual(load_sample_packet(), ORBITAL_SERIES_B)

    def test_document_order_is_preserved(self) -> None:
        """Ordering survives intake, because the IR's ids are positional."""
        packet = load_sample_packet()
        self.assertEqual(
            [point.metric for point in packet.data_points],
            [point.metric for point in ORBITAL_SERIES_B.data_points],
        )

    def test_wrong_document_version_is_refused(self) -> None:
        """A document the slice does not understand is refused, not guessed at."""
        document = json.loads(read_document())
        document["document_version"] = "something-else/9.9"
        with self.assertRaises(ValueError):
            parse_document(json.dumps(document), origin="test")

    def test_missing_required_field_is_refused(self) -> None:
        """Structural gaps fail loudly rather than defaulting silently."""
        document = json.loads(read_document())
        del document["company_name"]
        with self.assertRaises(ValueError):
            parse_document(json.dumps(document), origin="test")

    def test_malformed_json_is_refused(self) -> None:
        """A document that is not JSON fails at intake, not downstream."""
        with self.assertRaises(ValueError):
            parse_document("{not json", origin="test")

    def test_document_declares_the_expected_version(self) -> None:
        """The committed sample matches the format the parser accepts."""
        self.assertEqual(
            json.loads(read_document())["document_version"], DOCUMENT_VERSION
        )


class TestSliceExecution(unittest.TestCase):
    """One document traverses the complete pipeline."""

    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.output_root = Path(self._temporary.name)
        self.addCleanup(self._temporary.cleanup)

    def test_every_stage_artifact_is_written(self) -> None:
        """Each stage can be inspected on its own."""
        run = slice_run.execute_slice(output_root=self.output_root)
        for path in run.artifact_paths:
            with self.subTest(artifact=path.name):
                self.assertTrue(path.is_file())
                self.assertGreater(path.stat().st_size, 0)

    def test_stage_artifacts_cover_the_whole_pipeline(self) -> None:
        """Document, packet, IR, artifacts, record and report are all present."""
        run = slice_run.execute_slice(output_root=self.output_root)
        self.assertEqual(
            [path.name for path in run.artifact_paths], list(slice_run.STAGE_FILES)
        )

    def test_artifacts_are_independently_readable(self) -> None:
        """Each JSON artifact parses on its own, without the others."""
        run = slice_run.execute_slice(output_root=self.output_root)
        directory = run.output_directory

        document = json.loads((directory / slice_run.DOCUMENT_FILE).read_text("utf-8"))
        packet = json.loads((directory / slice_run.PACKET_FILE).read_text("utf-8"))
        ir = json.loads((directory / slice_run.IR_FILE).read_text("utf-8"))
        artifacts = json.loads(
            (directory / slice_run.ARTIFACTS_FILE).read_text("utf-8")
        )
        record = json.loads((directory / slice_run.RECORD_FILE).read_text("utf-8"))

        self.assertEqual(document["id"], ORBITAL_SERIES_B.id)
        self.assertEqual(packet["id"], ORBITAL_SERIES_B.id)
        self.assertEqual(ir["metadata"]["packet_id"], ORBITAL_SERIES_B.id)
        self.assertEqual(len(artifacts), len(investment.DOMAIN.kernels))
        self.assertEqual(sorted(record), ["artifacts", "ir", "synthesis", "trace"])

    def test_persisted_record_matches_the_live_record(self) -> None:
        """The written record is the record the pipeline produced, not a copy of it.

        Recomputed from a fresh in-memory execution and compared, so a
        serialisation bug cannot hide behind a self-consistent file.
        """
        run = slice_run.execute_slice(output_root=self.output_root)
        result, synthesis = execute(ORBITAL_SERIES_B, investment.DOMAIN)

        written = json.loads(
            (run.output_directory / slice_run.RECORD_FILE).read_text("utf-8")
        )
        self.assertEqual(written["ir"], slice_run._canonical(result.ir))
        self.assertEqual(written["artifacts"], slice_run._canonical(result.artifacts))
        self.assertEqual(written["synthesis"], slice_run._canonical(synthesis))
        self.assertEqual(written["trace"], slice_run._canonical(result.trace))

    def test_report_is_the_canonical_projection(self) -> None:
        """The final report is the prototype's own renderer, unaltered."""
        from choir_prototype.core.report import render

        run = slice_run.execute_slice(output_root=self.output_root)
        result, synthesis = execute(ORBITAL_SERIES_B, investment.DOMAIN)
        written = (run.output_directory / slice_run.REPORT_FILE).read_text("utf-8")
        self.assertEqual(written, render(result, synthesis) + "\n")

    def test_report_reaches_a_recommendation(self) -> None:
        """The slice produces a judgment, not an empty rendering."""
        run = slice_run.execute_slice(output_root=self.output_root)
        report = (run.output_directory / slice_run.REPORT_FILE).read_text("utf-8")
        self.assertIn("INSTITUTIONAL REASONING REPORT", report)
        self.assertIn("PROCEED WITH CONDITIONS", report)

    def test_metadata_records_every_stage(self) -> None:
        """Metadata names each artifact and its hash, so files can be checked."""
        run = slice_run.execute_slice(output_root=self.output_root)
        metadata = json.loads(
            (run.output_directory / slice_run.METADATA_FILE).read_text("utf-8")
        )
        self.assertEqual(metadata["record_digest"], run.record_digest)
        self.assertEqual(metadata["report_digest"], run.report_digest)
        self.assertEqual(
            [stage["file"] for stage in metadata["stages"]],
            list(slice_run.STAGE_FILES),
        )


class TestSliceDeterminism(unittest.TestCase):
    """The same document produces the same bytes on every run."""

    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.output_root = Path(self._temporary.name)
        self.addCleanup(self._temporary.cleanup)

    def test_repeat_runs_produce_identical_artifacts(self) -> None:
        """Re-running overwrites every artifact with identical bytes."""
        first = slice_run.execute_slice(output_root=self.output_root)
        before = {path.name: path.read_bytes() for path in first.artifact_paths}

        second = slice_run.execute_slice(output_root=self.output_root)
        after = {path.name: path.read_bytes() for path in second.artifact_paths}

        self.assertEqual(before, after)
        self.assertEqual(first.record_digest, second.record_digest)
        self.assertEqual(first.report_digest, second.report_digest)

    def test_metadata_is_stable(self) -> None:
        """No timestamp or run counter leaks into the persisted metadata."""
        run = slice_run.execute_slice(output_root=self.output_root)
        metadata_path = run.output_directory / slice_run.METADATA_FILE
        first = metadata_path.read_bytes()
        slice_run.execute_slice(output_root=self.output_root)
        self.assertEqual(first, metadata_path.read_bytes())

    def test_the_underlying_pipeline_still_replays(self) -> None:
        """The prototype's own replay checks still pass on the parsed packet."""
        report = verify(load_sample_packet(), investment.DOMAIN, runs=2)
        self.assertTrue(report.passed, [check.name for check in report.checks])


if __name__ == "__main__":
    unittest.main()
