"""The R-Fabric bridge: turning a finished R-Fabric run into a candidate D-Core can admit.

This module is the ruling on ``DECISION-005`` (see
``docs/architecture/DECISION-005_RULING_rfabric_evaluates.md`` at the
repository root): **R-Fabric evaluates; D-Core commits.** Neither of the two
options the ADR originally listed described this shape -- R-Fabric is not "DAALE
evaluating for itself" (the evaluator does not live in ``daale/``) and it is not
"the frozen ``choir_prototype`` kernels" (it calls models over the network and
produces a decision through its own deterministic policy engine, not through
the frozen synthesizer). It is a third answer, made explicit rather than
reached by implication, which is exactly what the ADR asked for.

What this module does *not* do is smaller than it looks
---------------------------------------------------------

It does not evaluate anything. R-Fabric has already run to completion --
kernels dispatched, an adversarial pass complete, a deterministic policy rule
selected -- by the time anything here executes. This module only translates
that finished, validated result into the two things the D-Core's existing
machinery already knows how to take: a CHOIR package for
``execution.contract.validate_package``, and one ``Candidate`` for
``execution.commit.run_gate``. The commit gate was not changed to accommodate
this; ``"rfabric"`` was already in ``DETERMINISTIC_ORIGINS`` and already the
default origin in the execution test suite's own candidate fixture
(``tests/test_execution.py``). This module is what finally produces one.

It also never imports R-Fabric's code -- only the plain JSON dict its pipeline
already writes to ``runs/``. That keeps the boundary the closure note states
for ``conformance/`` and ``execution/`` ("neither package imports the engine")
intact under its new meaning: D-Core does not import the evaluator, whichever
evaluator it turns out to be.

Two contracts, not one, and why that is named rather than hidden
------------------------------------------------------------------

R-Fabric's own ``CHOIR_CONTRACT_DRAFT.md`` says plainly that it is "not the
complete or canonical CHOIR specification." D-Core's contract module
transcribes the frozen v0.1 research freeze's commitment A2 -- a different,
canonical, and considerably older ontology. Translating R-Fabric's case /
policy / decision packet into the A2 shape (entities, claims, evidence,
assumptions, relationships, uncertainty, metadata) makes the result
*structurally* admissible to the gate; it does not make R-Fabric's draft
contract the same document as the v0.1 freeze. So the translated package
carries R-Fabric's own contract version string as its ``choir_version``
(``"CHOIR-CONTRACT-DRAFT-0.1"``), not ``"0.1"``. Anyone reading a committed
object back knows which contract actually produced it, rather than a version
string quietly overclaiming compliance with the canonical freeze -- the thing
the project's own rules name as something not to do.

What is still not solved by any of this
-----------------------------------------

- The state store is in-memory (v0's recorded limitation). Each admission
  here opens a fresh ``ReasoningStateStore``, so repeated runs against the
  same case do not yet version against each other the way they would once a
  persistence layer exists; every admission commits its object at version 1.
- Treating R-Fabric's decision packet as reproducible enough to skip
  escalation rests on its policy engine being a deterministic function of
  *validated* findings, not on the underlying model calls being
  deterministic. Two live runs with different model output can legitimately
  produce different candidates for the same case; each is judged on its own
  gate check, not against the other.
- This is still not a judgment. ``ExecutionSummary.emits_judgment`` is
  unaffected by anything here -- committing a policy state is not adjudicating
  one, and the decision packet says as much in its own
  ``authority_notice``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from daale.execution import (
    Candidate,
    ContractRejected,
    DCore,
    ExecutionSummary,
    GateOutcome,
    ReasoningStateStore,
)

# R-Fabric's decision packet is deterministic policy output, not model
# self-reported confidence, and origin="rfabric" was already reserved in
# DECISION-007's allow-list before anything produced a candidate carrying it.
ORIGIN = "rfabric"


def _analyst_findings(trace: Mapping[str, Any]) -> Mapping[str, Any]:
    """The analyst's provisional findings, or an empty mapping if absent."""
    return trace.get("provisional_findings", {}).get("analyst", {})


def _claim_evidence_relations(analyst: Mapping[str, Any]) -> dict[str, list[dict]]:
    """Map each case claim id to the evidence relations the analyst found."""
    return {
        entry["claim_id"]: entry.get("evidence_relations", [])
        for entry in analyst.get("claim_analyses", [])
    }


def _claim_uncertainties(analyst: Mapping[str, Any]) -> dict[str, list[str]]:
    """Map each case claim id to its recorded uncertainties, where any exist."""
    return {
        entry["claim_id"]: entry["uncertainties"]
        for entry in analyst.get("claim_analyses", [])
        if entry.get("uncertainties")
    }


def build_choir_package(trace: Mapping[str, Any]) -> dict[str, Any]:
    """Translate one finished R-Fabric trace into a commitment-A2-shaped package.

    Structural translation only -- see the module docstring for what this
    does and does not claim about CHOIR compliance. Every identifier in the
    result comes from the case, the policy, or the analyst's own validated
    findings; nothing here invents a claim, a requirement, or an evidence
    item R-Fabric did not already validate.
    """
    case = trace["case"]
    policy = trace["policy"]
    decision_packet = trace["decision_packet"]
    analyst = _analyst_findings(trace)
    relations_by_claim = _claim_evidence_relations(analyst)
    requirement_summary = decision_packet.get("requirement_summary", {})

    sources: dict[str, dict[str, Any]] = {}
    for item in case["evidence"]:
        source = item["source"]
        sources[source["source_id"]] = source
    entities = [
        {
            "id": source_id,
            "label": source["title"],
            "source_type": source["source_type"],
        }
        for source_id, source in sorted(sources.items())
    ]

    evidence = [
        {
            "id": item["evidence_id"],
            "text": item["text"],
            "source": item["source"]["source_id"],
        }
        for item in case["evidence"]
    ]

    claims: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []

    for item in case["claims"]:
        claim_id = item["claim_id"]
        relations = relations_by_claim.get(claim_id, [])
        claims.append(
            {
                "id": claim_id,
                "text": item["text"],
                "kind": "case_claim",
                "cites": [relation["evidence_id"] for relation in relations],
            }
        )
        for relation in relations:
            relationships.append(
                {
                    "source": claim_id,
                    "target": relation["evidence_id"],
                    "relation": relation["relation"],
                }
            )

    for requirement in policy["requirements"]:
        requirement_id = requirement["requirement_id"]
        summary = requirement_summary.get(requirement_id, {})
        cited_evidence = summary.get("evidence_ids", [])
        claims.append(
            {
                "id": requirement_id,
                "text": requirement["description"],
                "kind": "policy_requirement",
                "cites": cited_evidence,
                "requirement_status": summary.get("status", "UNKNOWN"),
            }
        )
        relation = "SUPPORTS" if summary.get("status") == "SATISFIED" else "WEAKENS"
        for evidence_id in cited_evidence:
            relationships.append(
                {"source": requirement_id, "target": evidence_id, "relation": relation}
            )

    case_id = case["case_id"]
    assumptions = [
        {"id": f"ASM-{case_id}-{index + 1}", "label": text}
        for index, text in enumerate(analyst.get("assumptions", []))
    ]

    package: dict[str, Any] = {
        "choir_version": trace["choir_contract_version"],
        "entities": entities,
        "claims": claims,
        "evidence": evidence,
        "assumptions": assumptions,
        "relationships": relationships,
        "uncertainty": _claim_uncertainties(analyst),
        "metadata": {
            "case_id": case_id,
            "decision_stage": case["decision_stage"],
            "decision_question": case["decision_question"],
            "policy_id": policy["policy_id"],
            "policy_version": policy["policy_version"],
            "rfabric_run_id": trace["run"]["run_id"],
            "rfabric_daale_version": trace["daale_version"],
            "adversarial_summary": decision_packet.get("adversarial_summary", ""),
            "authority_notice": decision_packet.get("authority_notice", ""),
        },
    }
    return package


def build_candidate(
    trace: Mapping[str, Any], execution_id: str, store: ReasoningStateStore
) -> Candidate:
    """Build the one candidate this run proposes: its deterministic decision packet.

    ``object_id`` is keyed on the case, not the run, so that a persistence
    layer (not yet built -- see the module docstring) could one day version
    successive runs against the same case rather than treating each as an
    unrelated object. ``read_versions`` reads whatever the store currently
    holds for that object so the gate's staleness check means something
    the moment persistence exists, instead of being wired in later as an
    afterthought.
    """
    decision_packet = trace["decision_packet"]
    case_id = decision_packet["case_id"]
    object_id = f"rfabric-judgment:{case_id}"

    provenance = tuple(
        sorted(
            set(decision_packet.get("provisional_claim_statuses", {}))
            | {
                evidence_id
                for requirement in decision_packet.get(
                    "requirement_summary", {}
                ).values()
                for evidence_id in requirement.get("evidence_ids", [])
            }
        )
    )

    current_version = store.current_version(object_id)
    read_versions = {} if current_version is None else {object_id: current_version}

    return Candidate(
        candidate_id=f"rfabric-candidate:{trace['run']['run_id']}",
        execution_id=execution_id,
        object_id=object_id,
        payload=decision_packet,
        provenance=provenance,
        read_versions=read_versions,
        origin=ORIGIN,
    )


@dataclass(frozen=True)
class Admission:
    """What happened when one R-Fabric trace was offered to the D-Core."""

    summary: ExecutionSummary
    outcome: GateOutcome


def admit(trace: Mapping[str, Any]) -> Admission:
    """Run one finished R-Fabric trace through the D-Core, start to close.

    Opens a fresh execution over the translated package, proposes the one
    decision-packet candidate the run produced, and closes. Raises
    ``ContractRejected`` if the translated package itself is not admissible --
    which would indicate a bug in ``build_choir_package``, since R-Fabric's own
    validation already guarantees the inputs this function reads from.
    """
    store = ReasoningStateStore()
    core = DCore(store)
    package = build_choir_package(trace)

    identity = core.open_execution(package["choir_version"], package)
    candidate = build_candidate(trace, identity.execution_id, store)
    outcome = core.admit(candidate)
    summary = core.close()
    return Admission(summary=summary, outcome=outcome)


def render(admission: Admission) -> str:
    """Lay the admission out as text. A projection; it decides nothing."""
    summary = admission.summary
    outcome = admission.outcome
    lines = [
        f"execution:        {summary.identity.execution_id}",
        f"choir_version:    {summary.identity.choir_version}",
        f"candidate:        {outcome.candidate.candidate_id}",
        f"object:           {outcome.candidate.object_id}",
        f"origin:           {outcome.candidate.origin}",
        f"state:            {outcome.state.value}",
        f"insufficient_basis: {summary.insufficient_basis}",
        f"emits_judgment:   {summary.emits_judgment}",
        "",
        "gate checks:",
    ]
    for check in outcome.checks:
        lines.append(f"  {check.status.value:<9} {check.name} -- {check.detail}")
    lines.append("")
    lines.append("trace:")
    lines.append(summary.trace and "\n".join(
        f"  {event.sequence:>3}  {event.kind:<26} {event.subject}"
        + (f" -- {event.detail}" if event.detail else "")
        for event in summary.trace
    ) or "  (empty)")
    return "\n".join(lines)


def as_json(admission: Admission) -> dict[str, Any]:
    """Render the admission as a JSON-safe mapping, for the artifact on disk."""
    summary = admission.summary
    outcome = admission.outcome
    return {
        "execution_id": summary.identity.execution_id,
        "choir_version": summary.identity.choir_version,
        "input_digest": summary.identity.input_digest,
        "candidate_id": outcome.candidate.candidate_id,
        "object_id": outcome.candidate.object_id,
        "origin": outcome.candidate.origin,
        "state": outcome.state.value,
        "committed": list(summary.committed),
        "rejected": list(summary.rejected),
        "review_required": list(summary.review_required),
        "insufficient_basis": summary.insufficient_basis,
        "emits_judgment": summary.emits_judgment,
        "judgment_unavailable_because": summary.judgment_unavailable_because,
        "gate_checks": [
            {"name": check.name, "status": check.status.value, "detail": check.detail}
            for check in outcome.checks
        ],
        "trace": [
            {
                "sequence": event.sequence,
                "kind": event.kind,
                "subject": event.subject,
                "detail": event.detail,
            }
            for event in summary.trace
        ],
        "payload": dict(outcome.candidate.payload),
    }


__all__ = [
    "ORIGIN",
    "Admission",
    "admit",
    "as_json",
    "build_candidate",
    "build_choir_package",
    "render",
]
