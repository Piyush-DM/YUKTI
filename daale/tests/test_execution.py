"""Tests for the DAALE v0 D-Core, state store, trace and commit gate.

The tests that matter most here are the ones defending properties that fail
silently when they break: an execution identity that collides, a proposal that
reaches canonical state without passing the gate, and a boundary that erodes
because someone added one convenient method.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

from daale.conformance import COMMITMENTS
from daale.execution import (
    IR_SECTIONS,
    Candidate,
    CandidateState,
    CheckStatus,
    ContractRejected,
    DCore,
    ExecutionLease,
    ReasoningStateStore,
    StaleWrite,
    UnauthorizedWrite,
    compute_input_digest,
    identify,
    run_gate,
    validate_package,
)
from daale.execution import trace as events

ROOT = Path(__file__).resolve().parents[2]
CHOIR_VERSION = "0.1"


def package(**overrides: Any) -> dict[str, Any]:
    """A minimal package satisfying the A2 contract."""
    built: dict[str, Any] = {
        "choir_version": CHOIR_VERSION,
        "entities": [{"id": "ent-001", "label": "Orbital"}],
        "claims": [{"id": "clm-001", "cites": ["ev-001"], "about": "ent-001"}],
        "evidence": [{"id": "ev-001", "status": "reported", "value": 42}],
        "assumptions": [{"id": "asm-001", "label": "market holds"}],
        "relationships": [{"source": "clm-001", "target": "ent-001"}],
        "uncertainty": {"clm-001": "likely"},
        "metadata": {"packet": "sample"},
    }
    built.update(overrides)
    return built


def candidate(**overrides: Any) -> Candidate:
    """A candidate that passes every active gate check by default."""
    fields: dict[str, Any] = {
        "candidate_id": "cnd-001",
        "execution_id": "",
        "object_id": "obj-001",
        "payload": {"finding": "supported"},
        "provenance": ("ev-001",),
        "read_versions": {},
        "origin": "rfabric",
    }
    fields.update(overrides)
    return Candidate(**fields)


class TestExecutionIdentity(unittest.TestCase):
    """Identity is bound to inputs, at full fidelity, before anything is lost."""

    def test_the_same_package_names_the_same_execution(self) -> None:
        self.assertEqual(
            identify(CHOIR_VERSION, package()).execution_id,
            identify(CHOIR_VERSION, package()).execution_id,
        )

    def test_inputs_the_engine_would_flatten_are_still_distinct(self) -> None:
        """The DECISION-006 collision, as a regression test.

        A figure recorded as ``reported`` and the same figure recorded as
        ``estimated`` produced an identical ``record_digest``, because the
        frozen translator maps both to ``Uncertainty.LIKELY``. An identifier
        derived from output could not tell them apart. One derived from input
        must.
        """
        reported = package()
        estimated = package(
            evidence=[{"id": "ev-001", "status": "estimated", "value": 42}]
        )
        self.assertNotEqual(
            compute_input_digest(reported), compute_input_digest(estimated)
        )
        self.assertNotEqual(
            identify(CHOIR_VERSION, reported).execution_id,
            identify(CHOIR_VERSION, estimated).execution_id,
        )

    def test_reordering_is_a_different_execution(self) -> None:
        """Identifiers downstream are positional, so order is part of identity."""
        one = package(
            claims=[{"id": "clm-001"}, {"id": "clm-002"}],
        )
        other = package(
            claims=[{"id": "clm-002"}, {"id": "clm-001"}],
        )
        self.assertNotEqual(
            identify(CHOIR_VERSION, one).execution_id,
            identify(CHOIR_VERSION, other).execution_id,
        )

    def test_the_choir_version_participates(self) -> None:
        """The same package under a different theory version is a different run."""
        self.assertNotEqual(
            identify("0.1", package()).execution_id,
            identify("0.2", package()).execution_id,
        )

    def test_inputs_are_recorded_beside_the_identifier(self) -> None:
        """An identifier nobody can re-derive is an assertion, not a record."""
        identity = identify(CHOIR_VERSION, package())
        self.assertEqual(identity.input_digest, compute_input_digest(package()))


class TestContract(unittest.TestCase):
    """Structural admissibility, transcribed from commitment A2."""

    def test_the_contract_sections_match_commitment_a2(self) -> None:
        """The contract and the register must not drift apart.

        Both transcribe the same frozen sentence. If someone edits one, this
        fails rather than leaving two disagreeing copies of A2.
        """
        statement = next(
            c.statement for c in COMMITMENTS if c.commitment_id == "A2"
        ).lower()
        for section in IR_SECTIONS:
            with self.subTest(section=section):
                self.assertIn(section, statement)

    def test_a_well_formed_package_is_admissible(self) -> None:
        self.assertTrue(validate_package(package()).valid)

    def test_a_missing_section_is_a_violation(self) -> None:
        incomplete = package()
        del incomplete["relationships"]
        result = validate_package(incomplete)
        self.assertFalse(result.valid)
        self.assertIn("relationships", [v.subject for v in result.violations])

    def test_a_missing_choir_version_is_a_violation(self) -> None:
        without = package()
        del without["choir_version"]
        self.assertFalse(validate_package(without).valid)

    def test_a_duplicate_identifier_is_a_violation(self) -> None:
        """Two objects with one id make every downstream citation ambiguous."""
        clashing = package(
            claims=[{"id": "clm-001"}],
            evidence=[{"id": "clm-001"}],
        )
        result = validate_package(clashing)
        self.assertFalse(result.valid)
        self.assertIn("duplicate-identifier", [v.code for v in result.violations])

    def test_a_dangling_reference_is_a_violation(self) -> None:
        """Commitment X4 is unenforceable if the IR itself cites what it lacks."""
        dangling = package(claims=[{"id": "clm-001", "cites": ["ev-404"]}])
        result = validate_package(dangling)
        self.assertFalse(result.valid)
        self.assertIn("dangling-reference", [v.code for v in result.violations])

    def test_every_violation_is_reported_not_just_the_first(self) -> None:
        broken = package(claims=[{"id": "clm-001", "cites": ["ev-404", "ev-405"]}])
        del broken["metadata"]
        self.assertGreaterEqual(len(validate_package(broken).violations), 3)


class TestStateStoreAuthority(unittest.TestCase):
    """Only the open execution's lease may write canonical state."""

    def setUp(self) -> None:
        self.store = ReasoningStateStore()

    def test_nothing_commits_without_an_open_execution(self) -> None:
        with self.assertRaises(UnauthorizedWrite):
            self.store.commit(ExecutionLease("x"), "obj", {}, (), {})

    def test_a_forged_lease_is_refused(self) -> None:
        """Fabricating a lease is the obvious attack on 'only the D-Core commits'."""
        self.store.open_execution("real-execution")
        with self.assertRaises(UnauthorizedWrite):
            self.store.commit(ExecutionLease("forged"), "obj", {}, (), {})

    def test_executions_are_serialised(self) -> None:
        """Two open executions would be two writers, which is nondeterminism."""
        self.store.open_execution("first")
        with self.assertRaises(UnauthorizedWrite):
            self.store.open_execution("second")

    def test_versions_increment_on_each_commit(self) -> None:
        lease = self.store.open_execution("exec")
        self.store.commit(lease, "obj", {"v": 1}, ("in",), {})
        self.assertEqual(self.store.current_version("obj"), 1)
        self.store.commit(lease, "obj", {"v": 2}, ("in",), {"obj": 1})
        self.assertEqual(self.store.current_version("obj"), 2)

    def test_a_stale_read_cannot_overwrite(self) -> None:
        """The optimistic-concurrency guard the plan names at the commit gate."""
        lease = self.store.open_execution("exec")
        self.store.commit(lease, "obj", {"v": 1}, ("in",), {})
        self.store.commit(lease, "obj", {"v": 2}, ("in",), {"obj": 1})
        with self.assertRaises(StaleWrite):
            self.store.commit(lease, "obj", {"v": 3}, ("in",), {"obj": 1})

    def test_provenance_and_dependents_are_recorded(self) -> None:
        lease = self.store.open_execution("exec")
        self.store.commit(lease, "derived", {}, ("source-a", "source-b"), {})
        self.assertEqual(self.store.provenance_of("derived"), ("source-a", "source-b"))
        self.assertEqual(self.store.dependents_of("source-a"), ("derived",))

    def test_snapshots_are_append_only_and_do_not_move(self) -> None:
        """A snapshot taken during an execution stays readable afterwards."""
        lease = self.store.open_execution("exec")
        self.store.commit(lease, "obj", {"v": 1}, ("in",), {})
        first = self.store.take_snapshot(lease)
        self.store.commit(lease, "obj", {"v": 2}, ("in",), {"obj": 1})
        self.store.take_snapshot(lease)

        self.assertEqual(len(self.store.snapshots), 2)
        self.assertEqual(self.store.snapshots[0], first)
        self.assertEqual(first.objects[0].payload, {"v": 1})


class TestCommitGate(unittest.TestCase):
    """The seven checks, and what each of them refuses."""

    def setUp(self) -> None:
        self.store = ReasoningStateStore()
        self.lease = self.store.open_execution("exec-1")

    def _gate(self, **overrides: Any) -> tuple[CandidateState, tuple[Any, ...]]:
        fields: dict[str, Any] = {"execution_id": "exec-1"}
        fields.update(overrides)
        return run_gate(candidate(**fields), self.store, "exec-1")

    def test_every_check_appears_in_every_outcome(self) -> None:
        """A gate that reports only its failures hides what it did not check."""
        _, checks = self._gate()
        self.assertEqual(len(checks), 7)

    def test_the_plan_check_is_inactive_and_never_passes(self) -> None:
        """Phase 3 does not exist, and the record must say so rather than pass."""
        _, checks = self._gate()
        plan = next(c for c in checks if c.name == "respects-active-execution-plan")
        self.assertIs(plan.status, CheckStatus.INACTIVE)
        self.assertFalse(plan.blocking)

    def test_a_candidate_from_another_execution_is_rejected(self) -> None:
        decided, _ = self._gate(execution_id="exec-elsewhere")
        self.assertIs(decided, CandidateState.REJECTED)

    def test_a_candidate_without_provenance_is_rejected(self) -> None:
        """Every committed result must trace back to its inputs."""
        decided, checks = self._gate(provenance=())
        self.assertIs(decided, CandidateState.REJECTED)
        failed = [c.name for c in checks if c.blocking]
        self.assertIn("required-provenance-present", failed)

    def test_a_candidate_citing_an_absent_input_is_rejected(self) -> None:
        decided, checks = self._gate(read_versions={"never-committed": 1})
        self.assertIs(decided, CandidateState.REJECTED)
        failed = [c.name for c in checks if c.blocking]
        self.assertIn("inputs-exist-and-are-not-superseded", failed)

    def test_a_stale_candidate_is_rejected(self) -> None:
        self.store.commit(self.lease, "obj", {"v": 1}, ("in",), {})
        self.store.commit(self.lease, "obj", {"v": 2}, ("in",), {"obj": 1})
        decided, checks = self._gate(read_versions={"obj": 1})
        self.assertIs(decided, CandidateState.REJECTED)
        failed = [c.name for c in checks if c.blocking]
        self.assertIn("no-stale-write-or-race", failed)

    def test_a_non_deterministic_origin_escalates_rather_than_commits(self) -> None:
        """The plan's control for LLM authority leakage, made mechanical."""
        decided, _ = self._gate(origin="llm")
        self.assertIs(decided, CandidateState.REVIEW_REQUIRED)

    def test_a_deterministic_origin_validates(self) -> None:
        decided, _ = self._gate(origin="rfabric")
        self.assertIs(decided, CandidateState.VALIDATED)


class TestDCore(unittest.TestCase):
    """The control plane end to end."""

    def setUp(self) -> None:
        self.store = ReasoningStateStore()
        self.dcore = DCore(self.store)

    def test_a_valid_package_opens_an_execution_and_commits(self) -> None:
        identity = self.dcore.open_execution(CHOIR_VERSION, package())
        outcome = self.dcore.admit(candidate(execution_id=identity.execution_id))
        summary = self.dcore.close()

        self.assertIs(outcome.state, CandidateState.COMMITTED)
        self.assertEqual(summary.committed, ("obj-001",))
        self.assertFalse(summary.insufficient_basis)
        self.assertEqual(self.store.current_version("obj-001"), 1)

    def test_an_invalid_package_opens_nothing(self) -> None:
        """A rejected package must leave no execution and no state behind."""
        broken = package()
        del broken["claims"]
        with self.assertRaises(ContractRejected) as caught:
            self.dcore.open_execution(CHOIR_VERSION, broken)

        self.assertFalse(caught.exception.result.valid)
        self.assertIsNotNone(caught.exception.identity.execution_id)
        with self.assertRaises(RuntimeError):
            self.dcore.close()

    def test_a_rejected_candidate_leaves_canonical_state_untouched(self) -> None:
        """Proposals are not facts. This is the invariant in one assertion."""
        identity = self.dcore.open_execution(CHOIR_VERSION, package())
        outcome = self.dcore.admit(
            candidate(execution_id=identity.execution_id, provenance=())
        )
        summary = self.dcore.close()

        self.assertIs(outcome.state, CandidateState.REJECTED)
        self.assertIsNone(self.store.canonical("obj-001"))
        self.assertTrue(summary.insufficient_basis)

    def test_an_escalated_candidate_leaves_canonical_state_untouched(self) -> None:
        identity = self.dcore.open_execution(CHOIR_VERSION, package())
        outcome = self.dcore.admit(
            candidate(execution_id=identity.execution_id, origin="human")
        )
        self.dcore.close()

        self.assertIs(outcome.state, CandidateState.REVIEW_REQUIRED)
        self.assertIsNone(self.store.canonical("obj-001"))

    def test_committing_nothing_emits_insufficient_basis(self) -> None:
        self.dcore.open_execution(CHOIR_VERSION, package())
        summary = self.dcore.close()

        self.assertTrue(summary.insufficient_basis)
        kinds = [event.kind for event in summary.trace]
        self.assertIn(events.INSUFFICIENT_BASIS, kinds)

    def test_the_trace_is_deterministic(self) -> None:
        """Identical input, version and configuration; identical trace."""

        def run() -> tuple[tuple[str, str], ...]:
            core = DCore(ReasoningStateStore())
            identity = core.open_execution(CHOIR_VERSION, package())
            core.admit(candidate(execution_id=identity.execution_id))
            return tuple((e.kind, e.subject) for e in core.close().trace)

        self.assertEqual(run(), run())

    def test_the_trace_carries_no_clock(self) -> None:
        """A timestamp would make every trace unique and comparison worthless."""
        self.dcore.open_execution(CHOIR_VERSION, package())
        summary = self.dcore.close()
        sequences = [event.sequence for event in summary.trace]
        self.assertEqual(sequences, list(range(len(sequences))))


class TestDecisionBoundary(unittest.TestCase):
    """The DECISION-005 boundary, asserted rather than only documented."""

    def test_no_execution_ever_emits_a_judgment(self) -> None:
        """v0 terminates; it does not adjudicate, and it says why."""
        core = DCore(ReasoningStateStore())
        identity = core.open_execution(CHOIR_VERSION, package())
        core.admit(candidate(execution_id=identity.execution_id))
        summary = core.close()

        self.assertFalse(summary.emits_judgment)
        self.assertIn("DECISION-005", summary.judgment_unavailable_because)

    def test_the_d_core_has_no_evaluator(self) -> None:
        """A guard against the boundary eroding one convenient method at a time.

        Adding any of these to ``DCore`` would settle DECISION-005 by
        implication -- an evaluator inside DAALE is option A or B depending on
        what it calls, and neither has been ruled.
        """
        forbidden = {
            "evaluate",
            "reason",
            "run_kernels",
            "synthesise",
            "synthesize",
            "adjudicate",
            "emit_judgment",
        }
        present = forbidden.intersection(dir(DCore))
        self.assertEqual(present, set(), f"DCore grew an evaluator: {present}")

    def test_execution_never_imports_the_engine(self) -> None:
        """Same boundary as conformance, asserted the same mechanical way."""
        probe = (
            "import sys\n"
            "from daale.execution import DCore, ReasoningStateStore\n"
            "DCore(ReasoningStateStore())\n"
            "roots = {'choir_prototype', 'applications'}\n"
            "leaked = sorted(m for m in sys.modules if m.split('.')[0] in roots)\n"
            "print(','.join(leaked))\n"
        )
        result = subprocess.run(
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
