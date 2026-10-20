"""The frozen CHOIR v0.1 commitments, as a machine-readable register.

This is the upstream end of the traceability chain, and it is the first one the
repository has had. ``docs/traceability/TRACEABILITY_MATRIX.md`` records that it
"currently cannot" link specifications to artifacts because every
``choir/specifications/SPEC-*.md`` file is empty. That is true of the SPEC
files, but it is not true of the project: ``CHOIR_v0.1_RESEARCH_FREEZE.md`` §3
is accepted, frozen content, and it states twenty-eight commitments in a form
concrete enough to check. This module transcribes them.

What this module is, and is not
-------------------------------

It is a **transcription**, not an interpretation. Each entry carries the
commitment's identifier, its statement, the support status the freeze assigns
it (D / A / S), and the evidence in this repository that exercises it. No
commitment is restated, strengthened, weakened or merged. Where the freeze says
a commitment is only *specified*, this register cites no evidence, and the lock
reports it as unexercised rather than passing.

Why it can be built while ``DECISION-005`` is open
--------------------------------------------------

``DECISION-005`` prohibits implementation that assumes an answer to *what DAALE
is* (options A-D). Nothing here does. The commitments are CHOIR's, frozen, and
identical under every one of those options -- DAALE must conform to §3 whether
it becomes the reference implementation, remains a separate target, is retired
as a name, or is the product-side engine boundary. The register also imports
nothing from ``choir_prototype`` or ``applications``, which is the mechanical
form of that claim and is asserted by
``test_conformance_never_imports_the_engine``.

This follows the route the research freeze §9 already set out: "Until it is
resolved, DAALE implementation should attach to §3 commitments rather than to
prototype internals." That is exactly what this register does.

Evidence kinds
--------------

``test``
    A test class or test method name. Resolved by scanning source, never by
    importing it.
``check``
    A named verification surface -- a CLI flag such as ``--frozen``, or one of
    the four replay checks such as ``projection-integrity``.
``decision``
    An approved architecture decision note. Used where a commitment is
    established by governance rather than by execution: ``X3`` is true because
    ``DECISION-001`` ruled it, and no test can demonstrate it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# The three groups the freeze organises §3 into. Kept as the freeze names them.
EPISTEMIC = "epistemic"
ARCHITECTURAL = "architectural"
EXECUTION = "execution"


class Status(Enum):
    """How much support the freeze records for a commitment.

    Transcribed from §3: "D = demonstrated in the V0.1 prototype - A = assumed,
    not yet demonstrated - S = specified in research, not implemented."
    """

    DEMONSTRATED = "D"
    ASSUMED = "A"
    SPECIFIED = "S"


class EvidenceKind(Enum):
    """Where a piece of evidence lives, which decides how it is resolved."""

    TEST = "test"
    CHECK = "check"
    DECISION = "decision"


@dataclass(frozen=True)
class Evidence:
    """One named artifact claimed to exercise a commitment."""

    kind: EvidenceKind
    name: str


@dataclass(frozen=True)
class Commitment:
    """One frozen CHOIR v0.1 commitment and the evidence that exercises it."""

    commitment_id: str
    group: str
    statement: str
    status: Status
    evidence: tuple[Evidence, ...]


def _test(name: str) -> Evidence:
    """Cite a test class or test method by name."""
    return Evidence(EvidenceKind.TEST, name)


def _check(name: str) -> Evidence:
    """Cite a named verification surface: a CLI flag or a replay check."""
    return Evidence(EvidenceKind.CHECK, name)


def _decision(name: str) -> Evidence:
    """Cite an architecture decision note that must be approved to resolve."""
    return Evidence(EvidenceKind.DECISION, name)


# ---------------------------------------------------------------------------
# §3.1 Epistemic commitments
# ---------------------------------------------------------------------------

_EPISTEMIC: tuple[Commitment, ...] = (
    Commitment(
        "E1",
        EPISTEMIC,
        "Fidelity, not truth. CHOIR claims what a corpus says, never that it "
        "is correct.",
        Status.DEMONSTRATED,
        (_test("test_carries_no_stance_or_confidence"),),
    ),
    Commitment(
        "E2",
        EPISTEMIC,
        "Confidence is derived, never authored. No code path accepts a literal "
        "confidence value.",
        Status.DEMONSTRATED,
        (
            _test("TestDerivedConfidence"),
            _test("test_every_confidence_carries_a_derivation"),
            _test("test_carries_no_stance_or_confidence"),
        ),
    ),
    Commitment(
        "E3",
        EPISTEMIC,
        "Three confidence axes - extraction, interpretive, inferential - never "
        "collapsed.",
        Status.SPECIFIED,
        (),
    ),
    Commitment(
        "E4",
        EPISTEMIC,
        "Undercutting is not rebutting. Cancellation withdraws a rule; it does "
        "not assert the opposite.",
        Status.SPECIFIED,
        (),
    ),
    Commitment(
        "E5",
        EPISTEMIC,
        "Influence is second-order. It modulates edges and cannot assert conclusions.",
        Status.SPECIFIED,
        (),
    ),
    Commitment(
        "E6",
        EPISTEMIC,
        "Ambiguity is a first-class IR citizen. The compiler emits diagnostics "
        "rather than guessing.",
        Status.SPECIFIED,
        (),
    ),
    Commitment(
        "E7",
        EPISTEMIC,
        "Saturate, then adjudicate. Fire every rule before resolving anything.",
        Status.ASSUMED,
        (),
    ),
    Commitment(
        "E8",
        EPISTEMIC,
        "Vikalpa - terminating in a legitimate disjunction is a valid output.",
        Status.DEMONSTRATED,
        (
            _test("test_thin_packet_declines_to_conclude"),
            _test("test_insufficient_basis_reached_in_more_than_one_domain"),
        ),
    ),
    Commitment(
        "E9",
        EPISTEMIC,
        "Explanations are projections of the trace, never regenerated.",
        Status.DEMONSTRATED,
        (
            _check("projection-integrity"),
            _test("test_rendering_is_a_pure_projection"),
            _test("test_inspection_is_a_pure_projection"),
        ),
    ),
    Commitment(
        "E10",
        EPISTEMIC,
        "Neural retrieval, symbolic adjudication. Embeddings propose; they "
        "never conclude.",
        Status.ASSUMED,
        (),
    ),
    Commitment(
        "E11",
        EPISTEMIC,
        "Evidence independence is computed, not assumed. Correlated evidence "
        "is discounted.",
        Status.SPECIFIED,
        (),
    ),
    Commitment(
        "E12",
        EPISTEMIC,
        "Nothing is deleted. Defeated objects are marked and retained.",
        Status.DEMONSTRATED,
        (),
    ),
    Commitment(
        "E13",
        EPISTEMIC,
        "An unevaluated thing is never a false thing. Coverage gaps are reported.",
        Status.DEMONSTRATED,
        (
            _test("TestPredicateCoverage"),
            _test("test_reports_missing_predicates_on_a_thin_packet"),
            _test("test_artifact_view_names_missing_inputs"),
        ),
    ),
)


# ---------------------------------------------------------------------------
# §3.2 Architectural commitments
# ---------------------------------------------------------------------------

_ARCHITECTURAL: tuple[Commitment, ...] = (
    Commitment(
        "A1",
        ARCHITECTURAL,
        "The pipeline stages and their order. Changing the order changes what "
        "can be explained.",
        Status.DEMONSTRATED,
        (
            _check("--audit"),
            _test("test_covers_all_five_stages"),
            _test("test_trace_covers_every_pipeline_stage"),
            _test("test_trace_steps_are_contiguous"),
        ),
    ),
    Commitment(
        "A2",
        ARCHITECTURAL,
        "The IR shape: entities, claims, evidence, assumptions, relationships, "
        "uncertainty, metadata.",
        Status.DEMONSTRATED,
        (
            _test("test_produces_ir_covering_every_data_point"),
            _test("test_every_domain_produces_an_ir"),
            _test("test_ir_view_reports_integrity_checks"),
        ),
    ),
    Commitment(
        "A3",
        ARCHITECTURAL,
        "The kernel contract: ChoirIR -> Artifact. Kernel independence rests on it.",
        Status.DEMONSTRATED,
        (
            _check("--audit"),
            _test("TestKernelIndependence"),
            _test("test_every_domain_produces_one_artifact_per_kernel"),
        ),
    ),
    Commitment(
        "A4",
        ARCHITECTURAL,
        "Kernels cannot observe the packet, each other, or the synthesizer.",
        Status.DEMONSTRATED,
        (
            _test("test_kernel_result_does_not_depend_on_other_kernels"),
            _test("test_kernel_result_does_not_depend_on_dispatch_order"),
        ),
    ),
    Commitment(
        "A5",
        ARCHITECTURAL,
        "Confidence derivation, and the rule that it is never authored.",
        Status.DEMONSTRATED,
        (
            _check("--audit"),
            _test("TestDerivedConfidence"),
            _test("test_every_confidence_carries_a_derivation"),
        ),
    ),
    Commitment(
        "A6",
        ARCHITECTURAL,
        "The five decision rules and their ordering. Cross-domain identity "
        "rests on it.",
        Status.DEMONSTRATED,
        (
            _check("--audit"),
            _test("test_one_rule_ordering_serves_every_domain"),
            _test("test_every_decision_rule_is_exercised_somewhere"),
            _test("test_exactly_one_rule_fires"),
            _test("test_evaluation_stops_at_the_firing_rule"),
        ),
    ),
    Commitment(
        "A7",
        ARCHITECTURAL,
        "The core/domain boundary and its one-way dependency. Domain "
        "independence rests on it.",
        Status.DEMONSTRATED,
        (
            _check("--audit"),
            _test("TestLayering"),
            _test("test_core_never_imports_a_domain"),
            _test("test_no_domain_defines_its_own_reasoning_machinery"),
        ),
    ),
    Commitment(
        "A8",
        ARCHITECTURAL,
        "Renderers are pure projections of the record.",
        Status.DEMONSTRATED,
        (
            _check("projection-integrity"),
            _test("test_rendering_is_a_pure_projection"),
            _test("test_contains_every_required_section"),
        ),
    ),
    Commitment(
        "A9",
        ARCHITECTURAL,
        "Institutional confidence is the minimum across kernels, not the mean.",
        Status.DEMONSTRATED,
        (
            _test("test_confidence_is_the_minimum_not_the_average"),
            _test("test_weakest_kernel_caps_confidence_in_every_domain"),
        ),
    ),
    Commitment(
        "A10",
        ARCHITECTURAL,
        "Confidence takes the weakest evidence item, not the average.",
        Status.DEMONSTRATED,
        (
            _test("test_weakest_evidence_sets_the_ceiling"),
            _test("test_always_names_a_limiting_factor"),
        ),
    ),
    Commitment(
        "A11",
        ARCHITECTURAL,
        "CONTESTED and INSUFFICIENT_BASIS are first-class terminal outcomes.",
        Status.DEMONSTRATED,
        (
            _test("test_insufficient_basis_reached_in_more_than_one_domain"),
            _test("test_thin_packet_declines_to_conclude"),
            _test("test_outcomes_differ_across_domains"),
        ),
    ),
)


# ---------------------------------------------------------------------------
# §3.3 Execution commitments
# ---------------------------------------------------------------------------

_EXECUTION: tuple[Commitment, ...] = (
    Commitment(
        "X1",
        EXECUTION,
        "Determinism: no clock, no randomness, no I/O, no concurrency, no "
        "dictionary-order dependence.",
        Status.DEMONSTRATED,
        (
            _check("--replay"),
            _check("execution-determinism"),
            _test("test_report_is_byte_identical_across_runs"),
            _test("test_both_packets_are_deterministic"),
            _test("test_every_domain_replays_identically"),
        ),
    ),
    Commitment(
        "X2",
        EXECUTION,
        "Replay: execution, report, inspection determinism, and projection "
        "integrity are separately checkable.",
        Status.DEMONSTRATED,
        (
            _check("execution-determinism"),
            _check("report-determinism"),
            _check("inspection-determinism"),
            _check("projection-integrity"),
            _test("test_verify_passes_for_both_packets"),
        ),
    ),
    Commitment(
        "X3",
        EXECUTION,
        "Deterministic kernels are the architecture. Model-backed execution is "
        "legacy and not canonical.",
        Status.DEMONSTRATED,
        (_decision("DECISION-001"),),
    ),
    Commitment(
        "X4",
        EXECUTION,
        "Kernels cite only identifiers present in the IR.",
        Status.DEMONSTRATED,
        (
            _test("TestArtifactValidation"),
            _test("test_rejects_fabricated_citation"),
            _test("test_rejects_silent_kernel"),
        ),
    ),
)


# Declaration order is canonical and is the order the freeze states them in.
COMMITMENTS: tuple[Commitment, ...] = _EPISTEMIC + _ARCHITECTURAL + _EXECUTION
