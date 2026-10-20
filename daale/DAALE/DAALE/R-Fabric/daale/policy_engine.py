"""Deterministic policy evaluation for validated DAALE findings."""

from collections import defaultdict

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
    for kernel_data in base_outputs.values():
        output = kernel_data["output"]
        for finding in output.get("findings", []):
            if finding["finding_type"] == "REQUIREMENT_ASSESSMENT":
                assessments.append({
                    "requirement_id": finding["target_id"],
                    "status": finding["status"],
                    "evidence_ids": finding["evidence_ids"],
                    "rationale": finding["content"],
                })
    return assessments


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
        claim_id: {"evidence_relations": [], "uncertainties": []}
        for claim_id in claim_ids
    }
    for kernel_data in base_outputs.values():
        output = kernel_data["output"]
        for finding in output.get("findings", []):
            target_id = finding["target_id"]
            if target_id not in claims:
                continue
            finding_type = finding["finding_type"]
            if finding_type == "CLAIM_ASSESSMENT":
                claims[target_id]["provisional_status"] = finding["status"]
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
            "evidence_relations": data["evidence_relations"],
            "uncertainties": data["uncertainties"],
        }
        for claim_id, data in claims.items()
    ]


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
        }
        for f in findings if f["finding_type"] == "CONTRADICTION"
    ]


def compute_metrics(case, policy, all_outputs):
    base_outputs = {k: v for k, v in all_outputs.items() if k != "ADVERSARY"}
    adversary = all_outputs.get("ADVERSARY", {}).get("output", {})

    requirement_by_id = {
        item["requirement_id"]: item for item in policy["requirements"]
    }
    assessments = _extract_requirement_assessments(base_outputs)
    assessment_by_id = {a["requirement_id"]: a for a in assessments}

    failed_critical = []
    failed_mandatory = []
    unknown_mandatory = []

    for requirement_id, requirement in requirement_by_id.items():
        status = assessment_by_id.get(requirement_id, {}).get("status", "UNKNOWN")
        if requirement["critical"] and status == "NOT_SATISFIED":
            failed_critical.append(requirement_id)
        if requirement["mandatory"] and status == "NOT_SATISFIED":
            failed_mandatory.append(requirement_id)
        if requirement["mandatory"] and status == "UNKNOWN":
            unknown_mandatory.append(requirement_id)

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
    high_contradictions = [
        item["contradiction_id"]
        for item in _extract_adversary_contradictions(adversary)
        if item["severity"] == "HIGH"
    ]

    mandatory_ids = [
        item["requirement_id"]
        for item in policy["requirements"]
        if item["mandatory"]
    ]
    all_mandatory_satisfied = all(
        assessment_by_id.get(req_id, {}).get("status") == "SATISFIED"
        for req_id in mandatory_ids
    )

    return {
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
        },
    }


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


def apply_policy(case, policy, all_outputs):
    metrics = compute_metrics(case, policy, all_outputs)
    rules = sorted(policy["rules"], key=lambda item: item["priority"], reverse=True)
    matching_rules = [rule for rule in rules if _condition_matches(rule["condition"], metrics)]

    if not matching_rules:
        raise DaaleValidationError("No policy rule matched the validated findings")

    selected_rule = matching_rules[0]
    base_outputs = {k: v for k, v in all_outputs.items() if k != "ADVERSARY"}
    assessments = _extract_requirement_assessments(base_outputs)
    claim_ids = {item["claim_id"] for item in case["claims"]}
    claim_analyses = _extract_claim_analyses(base_outputs, claim_ids)
    adversary = all_outputs.get("ADVERSARY", {}).get("output", {})

    requirement_summary = {
        item["requirement_id"]: {
            "status": item["status"],
            "evidence_ids": item["evidence_ids"],
            "rationale": item["rationale"],
        }
        for item in assessments
    }

    provisional_claims = {
        item["claim_id"]: item["provisional_status"]
        for item in claim_analyses
    }

    return {
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
        "adversarial_summary": adversary.get("adversarial_summary", ""),
        "authority_notice": (
            "This is a deterministic DAALE policy state, not an autonomous "
            "institutional decision. Authorized human review is required."
        ),
    }