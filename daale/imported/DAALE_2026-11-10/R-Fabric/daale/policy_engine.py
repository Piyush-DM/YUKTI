"""Deterministic policy evaluation for validated DAALE findings."""

from collections import defaultdict

from .evidence_integrity import adopted_injected_verdicts, screen_evidence
from .validation import DaaleValidationError


def _extract_requirement_assessments(base_outputs):
    """Extract requirement assessments from base kernels' findings.

    Reads the dedicated ``status`` field ``validate_kernel_output`` already
    requires on every REQUIREMENT_ASSESSMENT finding -- never ``content``,
    which is rationale prose and was never guaranteed to be one of
    ``REQUIREMENT_STATES`` verbatim. (It previously was read from
    ``content``, on the strength of an unenforced convention that only the
    hand-authored offline fixtures happened to follow; a real model writing
    an explanatory sentence there silently defeated every
    critical/mandatory-requirement check downstream. See the diagnostic
    session that added the ``status``/``relation`` fields.)
    """
    assessments = []
    for kernel_id, kernel_data in base_outputs.items():
        output = kernel_data["output"]
        for finding in output.get("findings", []):
            if finding["finding_type"] == "REQUIREMENT_ASSESSMENT":
                assessments.append({
                    "kernel_id": kernel_id,
                    "requirement_id": finding["target_id"],
                    "status": finding["status"],
                    "evidence_ids": finding["evidence_ids"],
                    "rationale": finding["content"],
                })
    return assessments


# Kernels whose focus includes assessing requirements are named first, so their reasoning is
# the one quoted when the kernels agree. The verdict itself never depends on this order.
_RATIONALE_ORDER = ("ANALYST", "FIRST_PRINCIPLES", "HISTORIAN")


def _kernel_rank(kernel_id):
    if kernel_id in _RATIONALE_ORDER:
        return (_RATIONALE_ORDER.index(kernel_id), kernel_id)
    return (len(_RATIONALE_ORDER), kernel_id)


def aggregate_requirement_assessments(policy, base_outputs):
    """One verdict for every policy requirement, from every base kernel that assessed it.

    Decided 2026-11-09, replacing "whichever kernel comes last wins":
      * no kernel assessed it            -> UNKNOWN
      * every assessing kernel agrees    -> that verdict
      * assessing kernels disagree       -> UNKNOWN, with the disagreement recorded

    A requirement is therefore SATISFIED or NOT_SATISFIED only when the kernels that looked at
    it agree. A contested requirement can never help an ADVANCE or hide behind a REJECT; on a
    mandatory requirement it becomes UNKNOWN, which the policy turns into a HOLD for a human.
    The result does not depend on kernel order or on the order of ``base_outputs``.

    Added 2026-11-12: a policy may set ``requirement_aggregation`` to ``unanimous_definite``.
    Under it UNKNOWN is an abstention, not a dissent:
      * SATISFIED and NOT_SATISFIED both present  -> UNKNOWN, disagreement recorded (unchanged)
      * one definite verdict, held by more kernels than abstained -> that verdict
      * otherwise                                                 -> UNKNOWN
    The live runs showed one kernel answering UNKNOWN against four that agreed, which the
    unanimous rule turned into a HOLD although no kernel had said the requirement was not met.
    Policies that do not set the field keep the unanimous rule, so their old runs replay as before.
    """
    mode = policy.get("requirement_aggregation", "unanimous")
    verdicts = defaultdict(dict)  # requirement_id -> kernel_id -> [assessments]
    for assessment in _extract_requirement_assessments(base_outputs):
        verdicts[assessment["requirement_id"]].setdefault(assessment["kernel_id"], []).append(assessment)

    summary = {}
    for requirement in policy["requirements"]:
        requirement_id = requirement["requirement_id"]
        by_kernel = verdicts.get(requirement_id, {})
        if not by_kernel:
            summary[requirement_id] = {
                "status": "UNKNOWN",
                "evidence_ids": [],
                "rationale": "No kernel assessed this requirement, so it is treated as UNKNOWN.",
                "assessed_by": {},
                "disagreement": False,
            }
            continue

        kernels = sorted(by_kernel, key=_kernel_rank)
        # A kernel that contradicts itself has no single verdict.
        assessed_by = {
            kernel_id: (
                by_kernel[kernel_id][0]["status"]
                if len({item["status"] for item in by_kernel[kernel_id]}) == 1
                else "UNKNOWN"
            )
            for kernel_id in kernels
        }
        cited = sorted({e for k in kernels for item in by_kernel[k] for e in item["evidence_ids"]})
        listed = "; ".join(f"{kernel_id}: {verdict}" for kernel_id, verdict in assessed_by.items())
        abstained = None
        if mode == "unanimous_definite":
            # UNKNOWN is a kernel saying it cannot tell, not a kernel saying the others are wrong.
            definite = {k: v for k, v in assessed_by.items() if v != "UNKNOWN"}
            abstained = sorted(k for k, v in assessed_by.items() if v == "UNKNOWN")
            distinct = set(definite.values())
            disagreement = len(distinct) > 1
            if disagreement:
                status = "UNKNOWN"
                rationale = f"Kernels disagree ({listed}), so the requirement is treated as UNKNOWN."
            elif not definite or len(definite) <= len(abstained):
                status = "UNKNOWN"
                rationale = (
                    f"Too few kernels reached a verdict ({listed}): a verdict needs more kernels "
                    "deciding than abstaining, so the requirement is treated as UNKNOWN."
                )
            else:
                status = next(iter(distinct))
                first = next(k for k in kernels if k in definite)
                rationale = by_kernel[first][0]["rationale"]
        else:
            distinct = set(assessed_by.values())
            disagreement = len(distinct) > 1
            status = "UNKNOWN" if disagreement else next(iter(distinct))
            if disagreement:
                rationale = f"Kernels disagree ({listed}), so the requirement is treated as UNKNOWN."
            else:
                rationale = by_kernel[kernels[0]][0]["rationale"]
        summary[requirement_id] = {
            "status": status,
            "evidence_ids": cited,
            "rationale": rationale,
            "assessed_by": assessed_by,
            "disagreement": disagreement,
        }
        if abstained is not None:
            summary[requirement_id]["abstained"] = abstained
    return summary


def _extract_claim_analyses(base_outputs, claim_ids):
    """Extract one claim analysis per declared case claim -- never per
    arbitrary finding target.

    Reads ``status`` (CLAIM_ASSESSMENT) and ``relation`` (EVIDENCE_RELATION)
    -- the dedicated verdict fields ``validate_kernel_output`` requires --
    never ``content``. See ``_extract_requirement_assessments`` for why
    reading ``content`` as if it were a closed-vocabulary verdict was the
    defect, not a style preference.

    ``claim_ids`` bounds which target ids are even eligible to become an
    entry here. The previous version keyed an unguarded ``defaultdict`` by
    whatever ``target_id`` a finding happened to name, for *any* finding
    type -- so a REQUIREMENT_ASSESSMENT's requirement id, an UNCERTAINTY
    finding's own id, or a concept a kernel invented mid-exploration all
    silently became a fabricated "claim" with a default
    INSUFFICIENT_EVIDENCE status nobody actually assessed. Confirmed live:
    ``R1``-``R4``, several ``UNC-*`` ids, and an invented ``soc2_equivalent``
    all leaked into ``provisional_claim_statuses`` this way in one run.
    ``validate_kernel_output`` now also requires EVIDENCE_RELATION findings
    to have ``target_type == "CLAIM"``, so the ``target_type`` check below
    is a second, defense-in-depth line on top of that -- not a duplicate.
    """
    claims = {
        claim_id: {"evidence_relations": [], "uncertainties": [], "status_by_kernel": {}}
        for claim_id in claim_ids
    }
    for kernel_id, kernel_data in base_outputs.items():
        output = kernel_data["output"]
        for finding in output.get("findings", []):
            target_id = finding["target_id"]
            if target_id not in claims:
                continue
            finding_type = finding["finding_type"]
            if finding_type == "CLAIM_ASSESSMENT":
                # Last kernel wins. Kept only for replaying traces recorded before 2026-11-17;
                # the decision packet now uses aggregate_claim_statuses (below).
                claims[target_id]["provisional_status"] = finding["status"]
                claims[target_id]["status_by_kernel"].setdefault(kernel_id, []).append(finding["status"])
            elif (
                finding_type == "EVIDENCE_RELATION"
                and finding["target_type"] == "CLAIM"
            ):
                claims[target_id]["evidence_relations"].append({
                    "evidence_id": finding["evidence_ids"][0] if finding["evidence_ids"] else "",
                    "relation": finding["relation"],
                    "rationale": finding["content"],
                })
            elif finding_type == "UNCERTAINTY":
                claims[target_id]["uncertainties"].append(finding["content"])

    return [
        {
            "claim_id": claim_id,
            "provisional_status": data.get("provisional_status", "INSUFFICIENT_EVIDENCE"),
            "status_by_kernel": data["status_by_kernel"],
            "evidence_relations": data["evidence_relations"],
            "uncertainties": data["uncertainties"],
        }
        for claim_id, data in claims.items()
    ]


def aggregate_claim_statuses(claim_analyses):
    """One status per declared claim, from every base kernel that assessed it.

    Added 2026-11-17, replacing "whichever kernel comes last wins" (the defect the requirement
    summary lost on 2026-11-09). In a live stress run four kernels assessed a claim CONTRADICTED and
    the one kernel that had followed an instruction hidden in the evidence, last in order, said
    SUPPORTED; the packet reported SUPPORTED.

      * no kernel assessed it           -> INSUFFICIENT_EVIDENCE
      * every assessing kernel agrees   -> that status
      * assessing kernels disagree      -> INSUFFICIENT_EVIDENCE, disagreement recorded

    The per-kernel split is always kept, so a reader sees who said what.
    """
    summary = {}
    for analysis in claim_analyses:
        by_kernel = analysis.get("status_by_kernel", {})
        kernels = sorted(by_kernel, key=_kernel_rank)
        # A kernel that contradicts itself has no single status.
        assessed_by = {
            kernel: (by_kernel[kernel][0] if len(set(by_kernel[kernel])) == 1 else "INSUFFICIENT_EVIDENCE")
            for kernel in kernels
        }
        distinct = set(assessed_by.values())
        disagreement = len(distinct) > 1
        if not distinct or disagreement:
            status = "INSUFFICIENT_EVIDENCE"
        else:
            status = next(iter(distinct))
        summary[analysis["claim_id"]] = {
            "status": status,
            "assessed_by": assessed_by,
            "disagreement": disagreement,
        }
    return summary


def _extract_adversary_challenges(adversary_output):
    """Extract CHALLENGE findings from adversary (unified schema)."""
    findings = adversary_output.get("findings", [])
    return [
        {
            "challenge_id": f["finding_id"],
            "target_type": f["target_type"],
            "target_id": f["target_id"],
            "challenge_type": f["status"],
            "severity": f["severity"],
            "evidence_ids": f["evidence_ids"],
            "reason": f["content"],
        }
        for f in findings if f["finding_type"] == "CHALLENGE"
    ]


def _extract_adversary_contradictions(adversary_output):
    """Extract CONTRADICTION findings from adversary (unified schema)."""
    findings = adversary_output.get("findings", [])
    return [
        {
            "contradiction_id": f["finding_id"],
            "claim_id": f["target_id"],
            "evidence_ids": f["evidence_ids"],
            "severity": f["severity"],
            "description": f["content"],
            "quotes": f.get("quotes") or [],
        }
        for f in findings if f["finding_type"] == "CONTRADICTION"
    ]


def _normalise_quote_text(text):
    text = str(text).casefold()
    for old, new in (("\u2018", "'"), ("\u2019", "'"), ("\u201c", '"'), ("\u201d", '"'), ("\u00a0", " ")):
        text = text.replace(old, new)
    return " ".join(text.split())


_MIN_QUOTE_CHARACTERS = 12


def contradiction_is_grounded(candidate, evidence_text_by_id):
    """True when the contradiction quotes, verbatim, at least two of the evidence items it cites.

    Added 2026-11-17. A contradiction needs two items that state incompatible things, so it must
    be able to show the words. Each quote must name an item the finding cites, be at least
    twelve characters, and appear in that item's text (case, spacing and curly quotes ignored; an
    ellipsis between fragments is allowed, each fragment checked). A model that draws an inference
    from one item, or paraphrases, cannot meet this. Deterministic: no model is consulted.
    """
    cited = set(candidate["evidence_ids"])
    grounded = set()
    for item in candidate.get("quotes") or []:
        evidence_id = item.get("evidence_id")
        if evidence_id not in cited or evidence_id not in evidence_text_by_id:
            continue
        text = _normalise_quote_text(item.get("quote", ""))
        fragments = [piece.strip(" .,;:") for piece in text.replace("\u2026", "...").split("...")]
        fragments = [piece for piece in fragments if piece]
        if sum(len(piece) for piece in fragments) < _MIN_QUOTE_CHARACTERS:
            continue
        source = _normalise_quote_text(evidence_text_by_id[evidence_id])
        if all(piece in source for piece in fragments):
            grounded.add(evidence_id)
    return len(grounded) >= 2


def _high_base_kernel_contradictions(base_outputs, already_counted):
    """HIGH CONTRADICTION findings raised by base kernels, one entry per distinct contradiction.

    Added 2026-11-17. In a live stress run CONTRARIAN and OUTSIDER each raised a HIGH contradiction
    between a reported leverage figure and a guarantee disclosed only in a note, and the metric
    counted zero because it read only the adversary's contradictions. Two kernels reporting the
    same contradiction (the same claim and the same evidence items) count once. Ids are prefixed
    with the kernel that raised them.
    """
    by_key = {}
    found = []
    for kernel_id in sorted(base_outputs, key=_kernel_rank):
        for finding in base_outputs[kernel_id]["output"].get("findings", []):
            if finding["finding_type"] != "CONTRADICTION" or finding["severity"] != "HIGH":
                continue
            key = (finding["target_id"], tuple(sorted(finding["evidence_ids"])))
            if key in by_key:
                # The same contradiction from a second kernel: keep the first id, but pool the quotes, so
                # that grounding (contradiction_grounding) is judged on what any kernel quoted. Without
                # this, a duplicate raised first without quotes would hide the same one raised with them.
                by_key[key]["quotes"] = by_key[key]["quotes"] + (finding.get("quotes") or [])
                continue
            entry = {
                "contradiction_id": f"{kernel_id}:{finding['finding_id']}",
                "evidence_ids": finding["evidence_ids"],
                "quotes": list(finding.get("quotes") or []),
            }
            by_key[key] = entry
            found.append(entry)
    return found


def compute_metrics(case, policy, all_outputs, *, include_alleged_critical_failures=True):
    base_outputs = {k: v for k, v in all_outputs.items() if k != "ADVERSARY"}
    adversary = all_outputs.get("ADVERSARY", {}).get("output", {})

    requirement_by_id = {
        item["requirement_id"]: item for item in policy["requirements"]
    }
    verdicts = aggregate_requirement_assessments(policy, base_outputs)

    failed_critical = []
    alleged_critical_failures = {}
    failed_mandatory = []
    unknown_mandatory = []

    for requirement_id, requirement in requirement_by_id.items():
        status = verdicts[requirement_id]["status"]
        if requirement["critical"] and status == "NOT_SATISFIED":
            failed_critical.append(requirement_id)
        if requirement["mandatory"] and status == "NOT_SATISFIED":
            failed_mandatory.append(requirement_id)
        if requirement["mandatory"] and status == "UNKNOWN":
            unknown_mandatory.append(requirement_id)

    if include_alleged_critical_failures:
        for assessment in _extract_requirement_assessments(base_outputs):
            requirement_id = assessment["requirement_id"]
            requirement = requirement_by_id[requirement_id]
            if (
                requirement["critical"]
                and assessment["status"] == "NOT_SATISFIED"
                and assessment["evidence_ids"]
            ):
                entry = alleged_critical_failures.setdefault(requirement_id, {})
                evidence_ids = entry.setdefault(assessment["kernel_id"], set())
                evidence_ids.update(assessment["evidence_ids"])

    relation_counts = defaultdict(int)
    claim_ids = {item["claim_id"] for item in case["claims"]}
    claim_analyses = _extract_claim_analyses(base_outputs, claim_ids)
    for claim_analysis in claim_analyses:
        for relation in claim_analysis.get("evidence_relations", []):
            rel = relation.get("relation")
            if rel in ("SUPPORTS", "WEAKENS", "CONTRADICTS", "CONTEXTUAL", "IRRELEVANT"):
                relation_counts[rel] += 1

    high_challenges = [
        item["challenge_id"]
        for item in _extract_adversary_challenges(adversary)
        if item["severity"] == "HIGH"
    ]
    high_candidates = [
        item
        for item in _extract_adversary_contradictions(adversary)
        if item["severity"] == "HIGH"
    ]
    if policy.get("contradiction_sources", "adversary") == "any_kernel":
        high_candidates += _high_base_kernel_contradictions(base_outputs, set())
    ungrounded_contradictions = None
    if policy.get("contradiction_grounding", "none") == "quoted":
        evidence_text = {item["evidence_id"]: item["text"] for item in case["evidence"]}
        grounded = [c for c in high_candidates if contradiction_is_grounded(c, evidence_text)]
        ungrounded_contradictions = [c["contradiction_id"] for c in high_candidates if c not in grounded]
        high_candidates = grounded
    high_contradictions = [c["contradiction_id"] for c in high_candidates]

    mandatory_ids = [
        item["requirement_id"]
        for item in policy["requirements"]
        if item["mandatory"]
    ]
    all_mandatory_satisfied = all(
        verdicts[req_id]["status"] == "SATISFIED"
        for req_id in mandatory_ids
    )

    metrics = {
        "high_adversarial_challenges": len(high_challenges),
        "high_unresolved_contradictions": len(high_contradictions),
        "failed_critical_requirements": len(failed_critical),
        "failed_mandatory_requirements": len(failed_mandatory),
        "unknown_mandatory_requirements": len(unknown_mandatory),
        "all_mandatory_requirements_satisfied": all_mandatory_satisfied,
        "supporting_relations": relation_counts["SUPPORTS"],
        "weakening_relations": relation_counts["WEAKENS"],
        "contradicting_relations": relation_counts["CONTRADICTS"],
        "always": True,
        "details": {
            "high_challenge_ids": high_challenges,
            "high_contradiction_ids": high_contradictions,
            "failed_critical_requirement_ids": sorted(failed_critical),
            "failed_mandatory_requirement_ids": sorted(failed_mandatory),
            "unknown_mandatory_requirement_ids": sorted(unknown_mandatory),
            "requirement_disagreement_ids": sorted(
                req_id for req_id, verdict in verdicts.items() if verdict["disagreement"]
            ),
            "unassessed_requirement_ids": sorted(
                req_id for req_id, verdict in verdicts.items() if not verdict["assessed_by"]
            ),
        },
    }
    # Present only under a policy that asks for grounding, so packets of other policies (and the
    # traces already recorded) keep exactly the metrics they had.
    if ungrounded_contradictions is not None:
        metrics["ungrounded_high_contradictions"] = len(ungrounded_contradictions)
        metrics["details"]["ungrounded_contradiction_ids"] = ungrounded_contradictions
    if include_alleged_critical_failures:
        metrics["alleged_critical_failures"] = len(alleged_critical_failures)
        metrics["details"]["alleged_critical_failure_ids"] = sorted(alleged_critical_failures)
        metrics["details"]["alleged_critical_failure_evidence"] = {
            requirement_id: {
                kernel_id: sorted(evidence_ids)
                for kernel_id, evidence_ids in sorted(by_kernel.items())
            }
            for requirement_id, by_kernel in sorted(alleged_critical_failures.items())
        }
    if policy.get("evidence_screening", "none") == "flag":
        flagged = screen_evidence(case)
        adopted = adopted_injected_verdicts(flagged, base_outputs)
        metrics["flagged_evidence_items"] = len(flagged)
        metrics["adopted_injected_verdicts"] = len(adopted)
        metrics["details"]["flagged_evidence"] = [
            {"evidence_id": item["evidence_id"], "flags": item["flags"]} for item in flagged
        ]
        metrics["details"]["adopted_injected_verdicts"] = adopted
    return metrics


def _condition_matches(condition, metrics):
    metric = condition["metric"]
    operator = condition["operator"]
    expected = condition["value"]
    actual = metrics[metric]

    if operator == "eq":
        return actual == expected
    if operator == "gte":
        return actual >= expected
    if operator == "lte":
        return actual <= expected
    raise DaaleValidationError(f"Unsupported policy operator: {operator}")


def apply_policy(
    case, policy, all_outputs, legacy_claim_statuses=False,
    include_alleged_critical_failures=True,
):
    """``legacy_claim_statuses`` reproduces the last-kernel-wins claim statuses of traces recorded
    before 2026-11-17, so that replay of those traces still agrees with what they recorded."""
    metrics = compute_metrics(
        case, policy, all_outputs,
        include_alleged_critical_failures=include_alleged_critical_failures,
    )
    rules = sorted(policy["rules"], key=lambda item: item["priority"], reverse=True)
    matching_rules = [rule for rule in rules if _condition_matches(rule["condition"], metrics)]

    if not matching_rules:
        raise DaaleValidationError("No policy rule matched the validated findings")

    selected_rule = matching_rules[0]
    base_outputs = {k: v for k, v in all_outputs.items() if k != "ADVERSARY"}
    claim_ids = {item["claim_id"] for item in case["claims"]}
    claim_analyses = _extract_claim_analyses(base_outputs, claim_ids)
    adversary = all_outputs.get("ADVERSARY", {}).get("output", {})

    # One entry per policy requirement, from the same aggregation the metrics use, so the
    # summary can never disagree with the decision that was made from it.
    requirement_summary = aggregate_requirement_assessments(policy, base_outputs)

    claim_summary = None
    if legacy_claim_statuses:
        provisional_claims = {
            item["claim_id"]: item["provisional_status"]
            for item in claim_analyses
        }
    else:
        claim_summary = aggregate_claim_statuses(claim_analyses)
        provisional_claims = {claim_id: entry["status"] for claim_id, entry in claim_summary.items()}

    packet = {
        "case_id": case["case_id"],
        "decision_stage": case["decision_stage"],
        "policy_id": policy["policy_id"],
        "policy_version": policy["policy_version"],
        "policy_state": selected_rule["outcome"],
        "triggered_rule": {
            "rule_id": selected_rule["rule_id"],
            "priority": selected_rule["priority"],
            "description": selected_rule["description"],
        },
        "other_matching_rule_ids": [
            rule["rule_id"] for rule in matching_rules[1:]
        ],
        "metrics": metrics,
        "requirement_summary": requirement_summary,
        "provisional_claim_statuses": provisional_claims,
        # The unified kernel schema names this field "summary"; the old
        # "adversarial_summary" key no longer exists, so this was always "".
        "adversarial_summary": adversary.get("summary", ""),
        "authority_notice": (
            "This is a deterministic DAALE policy state, not an autonomous "
            "institutional decision. Authorized human review is required."
        ),
    }
    if claim_summary is not None:
        packet["claim_summary"] = claim_summary
    return packet
