"""Structural and semantic validation for DAALE contracts."""

from jsonschema import Draft202012Validator

from .schemas import (
    ANALYST_OUTPUT_SCHEMA,
    CASE_SCHEMA,
    CLAIM_STATUSES,
    CHALLENGE_TYPES,
    CONTRADICTION_SEVERITIES,
    EVIDENCE_RELATIONS,
    KERNEL_FINDING_TYPES,
    KERNEL_IDS,
    KERNEL_OUTPUT_SCHEMA,
    POLICY_SCHEMA,
    REQUIREMENT_STATES,
    SEVERITIES,
)

# finding_type -> (the field that carries its verdict, the vocabulary that
# field must come from). "content" is rationale prose for every finding
# type; these three finding types additionally answer a specific closed
# question, and the policy engine must be able to read that answer without
# pattern-matching free text. A REQUIREMENT_ASSESSMENT finding answers
# SATISFIED / NOT_SATISFIED / UNKNOWN about a policy requirement; a
# CLAIM_ASSESSMENT finding answers SUPPORTED / CONTRADICTED /
# INSUFFICIENT_EVIDENCE about a case claim; an EVIDENCE_RELATION finding
# answers which of the five CHOIR relation kinds applies. Mixing any of
# these vocabularies would make the policy engine's own comparisons
# meaningless.
_VERDICT_FIELD_BY_FINDING_TYPE = {
    "REQUIREMENT_ASSESSMENT": ("status", REQUIREMENT_STATES),
    "CLAIM_ASSESSMENT": ("status", CLAIM_STATUSES),
    "EVIDENCE_RELATION": ("relation", EVIDENCE_RELATIONS),
    "CHALLENGE": ("status", CHALLENGE_TYPES),
    # CONTRADICTION has no separate verdict field -- its "content" is the
    # description of the contradiction, and severity indicates importance.
}


class DaaleValidationError(ValueError):
    """Raised when a DAALE boundary contract is violated."""


def validate_schema(instance, schema, label):
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda item: list(item.path))
    if not errors:
        return

    details = []
    for error in errors[:10]:
        path = ".".join(str(part) for part in error.absolute_path) or "<root>"
        details.append(f"{path}: {error.message}")
    remainder = len(errors) - len(details)
    if remainder > 0:
        details.append(f"...and {remainder} more validation error(s)")
    raise DaaleValidationError(f"{label} failed schema validation: " + " | ".join(details))


def _require_unique_ids(items, key, label):
    values = [item[key] for item in items]
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        raise DaaleValidationError(f"Duplicate {label}: {duplicates}")


def validate_case_and_policy(case, policy):
    validate_schema(case, CASE_SCHEMA, "Case")
    validate_schema(policy, POLICY_SCHEMA, "Policy")

    _require_unique_ids(case["claims"], "claim_id", "claim IDs")
    _require_unique_ids(case["evidence"], "evidence_id", "evidence IDs")
    _require_unique_ids(policy["requirements"], "requirement_id", "requirement IDs")
    _require_unique_ids(policy["rules"], "rule_id", "policy rule IDs")

    if case["decision_stage"] != policy["decision_stage"]:
        raise DaaleValidationError(
            "Case decision_stage does not match policy decision_stage: "
            f"{case['decision_stage']} != {policy['decision_stage']}"
        )

    priorities = [rule["priority"] for rule in policy["rules"]]
    if len(priorities) != len(set(priorities)):
        raise DaaleValidationError("Policy rule priorities must be unique")

    allowed_states = set(policy["decision_states"])
    undeclared_outcomes = sorted(
        {rule["outcome"] for rule in policy["rules"]} - allowed_states
    )
    if undeclared_outcomes:
        raise DaaleValidationError(
            f"Policy rules use undeclared decision states: {undeclared_outcomes}"
        )

    critical_optional = [
        requirement["requirement_id"]
        for requirement in policy["requirements"]
        if requirement["critical"] and not requirement["mandatory"]
    ]
    if critical_optional:
        raise DaaleValidationError(
            "Critical requirements must also be mandatory: "
            f"{critical_optional}"
        )

    fallback_rules = [
        rule
        for rule in policy["rules"]
        if rule["condition"]["metric"] == "always"
    ]
    if len(fallback_rules) != 1:
        raise DaaleValidationError("Policy must contain exactly one 'always' fallback rule")

    fallback_condition = fallback_rules[0]["condition"]
    if fallback_condition["operator"] != "eq" or fallback_condition["value"] is not True:
        raise DaaleValidationError("The 'always' fallback must use operator 'eq' and value true")

    boolean_metrics = {"all_mandatory_requirements_satisfied", "always"}
    for rule in policy["rules"]:
        condition = rule["condition"]
        metric = condition["metric"]
        value = condition["value"]
        if metric in boolean_metrics:
            if condition["operator"] != "eq" or not isinstance(value, bool):
                raise DaaleValidationError(
                    f"Rule {rule['rule_id']} must compare boolean metric {metric} "
                    "with operator 'eq' and a boolean value"
                )
        elif isinstance(value, bool):
            raise DaaleValidationError(
                f"Rule {rule['rule_id']} must compare numeric metric {metric} "
                "with a numeric value"
            )


def validate_analyst_output(analyst, case, policy):
    validate_schema(analyst, ANALYST_OUTPUT_SCHEMA, "Analyst output")

    if analyst["case_id"] != case["case_id"]:
        raise DaaleValidationError(
            f"Analyst case_id mismatch: {analyst['case_id']} != {case['case_id']}"
        )

    expected_claim_ids = {item["claim_id"] for item in case["claims"]}
    expected_evidence_ids = {item["evidence_id"] for item in case["evidence"]}
    expected_requirement_ids = {
        item["requirement_id"] for item in policy["requirements"]
    }

    _require_unique_ids(analyst["claim_analyses"], "claim_id", "analyst claim IDs")
    actual_claim_ids = {item["claim_id"] for item in analyst["claim_analyses"]}
    if actual_claim_ids != expected_claim_ids:
        raise DaaleValidationError(
            "Analyst must return every case claim exactly once. "
            f"Expected {sorted(expected_claim_ids)}, received {sorted(actual_claim_ids)}"
        )

    for claim_analysis in analyst["claim_analyses"]:
        relations = claim_analysis["evidence_relations"]
        _require_unique_ids(
            relations,
            "evidence_id",
            f"evidence IDs for claim {claim_analysis['claim_id']}",
        )
        related_ids = {item["evidence_id"] for item in relations}
        if related_ids != expected_evidence_ids:
            raise DaaleValidationError(
                f"Claim {claim_analysis['claim_id']} must classify every evidence item "
                f"exactly once. Expected {sorted(expected_evidence_ids)}, "
                f"received {sorted(related_ids)}"
            )

    _require_unique_ids(
        analyst["requirement_assessments"],
        "requirement_id",
        "analyst requirement IDs",
    )
    actual_requirement_ids = {
        item["requirement_id"] for item in analyst["requirement_assessments"]
    }
    if actual_requirement_ids != expected_requirement_ids:
        raise DaaleValidationError(
            "Analyst must assess every policy requirement exactly once. "
            f"Expected {sorted(expected_requirement_ids)}, "
            f"received {sorted(actual_requirement_ids)}"
        )

    for assessment in analyst["requirement_assessments"]:
        cited_ids = set(assessment["evidence_ids"])
        unknown_ids = cited_ids - expected_evidence_ids
        if unknown_ids:
            raise DaaleValidationError(
                f"Requirement {assessment['requirement_id']} cites unknown evidence: "
                f"{sorted(unknown_ids)}"
            )
        if assessment["status"] != "UNKNOWN" and not cited_ids:
            raise DaaleValidationError(
                f"Requirement {assessment['requirement_id']} is "
                f"{assessment['status']} but cites no evidence"
            )


def validate_adversary_output(adversary, case, policy):
    """Validate adversary output using the unified KERNEL_OUTPUT_SCHEMA.

    The adversary kernel now produces findings with types CHALLENGE and
    CONTRADICTION under the same schema as base kernels. This function
    delegates to validate_kernel_output for structural validation, then adds
    adversary-specific semantic checks.
    """
    # Structural + common semantic validation (finding types, target types,
    # evidence IDs, verdict fields, severity, confidence, relation matrix)
    validate_kernel_output(adversary, case, policy, "ADVERSARY")

    if adversary["kernel_id"] != "ADVERSARY":
        raise DaaleValidationError(
            f"Adversary output must have kernel_id 'ADVERSARY', got {adversary['kernel_id']!r}"
        )

    claim_ids = {item["claim_id"] for item in case["claims"]}
    evidence_ids = {item["evidence_id"] for item in case["evidence"]}
    requirement_ids = {item["requirement_id"] for item in policy["requirements"]}

    # Adversary-specific: only CHALLENGE and CONTRADICTION finding types allowed
    for finding in adversary["findings"]:
        ftype = finding["finding_type"]
        if ftype not in ("CHALLENGE", "CONTRADICTION"):
            raise DaaleValidationError(
                f"ADVERSARY: Finding {finding['finding_id']} has invalid "
                f"finding_type for adversary: {ftype!r} -- must be CHALLENGE or CONTRADICTION"
            )

        if ftype == "CHALLENGE":
            # CHALLENGE: target_type in {CLAIM, REQUIREMENT}, status in CHALLENGE_TYPES
            if finding["target_type"] not in ("CLAIM", "REQUIREMENT"):
                raise DaaleValidationError(
                    f"ADVERSARY: CHALLENGE finding {finding['finding_id']} must have "
                    f"target_type CLAIM or REQUIREMENT, got {finding['target_type']!r}"
                )
            valid_targets = claim_ids if finding["target_type"] == "CLAIM" else requirement_ids
            if finding["target_id"] not in valid_targets:
                raise DaaleValidationError(
                    f"ADVERSARY: CHALLENGE finding {finding['finding_id']} targets unknown "
                    f"{finding['target_type'].lower()} ID: {finding['target_id']!r}"
                )
            if finding.get("status") not in CHALLENGE_TYPES:
                raise DaaleValidationError(
                    f"ADVERSARY: CHALLENGE finding {finding['finding_id']} must have "
                    f"status in {CHALLENGE_TYPES}, got {finding.get('status')!r}"
                )

        elif ftype == "CONTRADICTION":
            # CONTRADICTION: target_type = CLAIM, content = description, min 2 evidence_ids
            if finding["target_type"] != "CLAIM":
                raise DaaleValidationError(
                    f"ADVERSARY: CONTRADICTION finding {finding['finding_id']} must have "
                    f"target_type CLAIM, got {finding['target_type']!r}"
                )
            if finding["target_id"] not in claim_ids:
                raise DaaleValidationError(
                    f"ADVERSARY: CONTRADICTION finding {finding['finding_id']} references "
                    f"unknown claim: {finding['target_id']!r}"
                )
            ev_ids = finding["evidence_ids"]
            if len(ev_ids) < 2:
                raise DaaleValidationError(
                    f"ADVERSARY: CONTRADICTION finding {finding['finding_id']} must cite "
                    f"at least two evidence items, got {len(ev_ids)}"
                )
            unknown = set(ev_ids) - evidence_ids
            if unknown:
                raise DaaleValidationError(
                    f"ADVERSARY: CONTRADICTION finding {finding['finding_id']} cites unknown "
                    f"evidence: {sorted(unknown)}"
                )
            if finding.get("severity") not in CONTRADICTION_SEVERITIES:
                raise DaaleValidationError(
                    f"ADVERSARY: CONTRADICTION finding {finding['finding_id']} has invalid "
                    f"severity: {finding.get('severity')!r}"
                )

        # Evidence citation check for both types
        unknown_evidence = set(finding["evidence_ids"]) - evidence_ids
        if unknown_evidence:
            raise DaaleValidationError(
                f"ADVERSARY: Finding {finding['finding_id']} cites unknown evidence: "
                f"{sorted(unknown_evidence)}"
            )


def validate_kernel_output(kernel_output, case, policy, kernel_id):
    validate_schema(kernel_output, KERNEL_OUTPUT_SCHEMA, f"{kernel_id} kernel output")

    if kernel_output["case_id"] != case["case_id"]:
        raise DaaleValidationError(
            f"{kernel_id} case_id mismatch: {kernel_output['case_id']} != {case['case_id']}"
        )

    if kernel_output["kernel_id"] != kernel_id:
        raise DaaleValidationError(
            f"Kernel output kernel_id mismatch: {kernel_output['kernel_id']} != {kernel_id}"
        )

    claim_ids = {item["claim_id"] for item in case["claims"]}
    evidence_ids = {item["evidence_id"] for item in case["evidence"]}
    requirement_ids = {item["requirement_id"] for item in policy["requirements"]}
    valid_target_ids = claim_ids | requirement_ids | evidence_ids | {"POLICY", "GENERAL"}

    finding_ids = [f["finding_id"] for f in kernel_output["findings"]]
    duplicates = sorted({fid for fid in finding_ids if finding_ids.count(fid) > 1})
    if duplicates:
        raise DaaleValidationError(f"{kernel_id}: Duplicate finding_ids: {duplicates}")

    for finding in kernel_output["findings"]:
        if finding["finding_type"] not in KERNEL_FINDING_TYPES:
            raise DaaleValidationError(
                f"{kernel_id}: Unknown finding_type: {finding['finding_type']}"
            )

        target_type = finding["target_type"]
        target_id = finding["target_id"]
        finding_type = finding["finding_type"]

        # A CLAIM_ASSESSMENT is an assessment of a declared case claim, and a
        # REQUIREMENT_ASSESSMENT is an assessment of a declared policy
        # requirement -- not of a POLICY- or GENERAL-scoped concept a kernel
        # invented in the middle of exploring (e.g. target_type "POLICY",
        # target_id "RISK_APPETITE"). Without this, such a finding was
        # structurally valid and leaked a fabricated identifier straight into
        # policy_engine.py's provisional_claim_statuses, alongside the real
        # claims. Confirmed live: an exploratory kernel emitted exactly this.
        required_target_type = {
            "CLAIM_ASSESSMENT": "CLAIM",
            "REQUIREMENT_ASSESSMENT": "REQUIREMENT",
            # CHOIR_CONTRACT_DRAFT.md defines an evidence relation as "the
            # relationship between one evidence item and one claim" --
            # never a requirement, policy, or general concept.
            "EVIDENCE_RELATION": "CLAIM",
        }.get(finding_type)
        if required_target_type is not None and target_type != required_target_type:
            raise DaaleValidationError(
                f"{kernel_id}: {finding_type} finding {finding['finding_id']} "
                f"must have target_type {required_target_type!r} -- it names "
                f"a declared {required_target_type.lower()}, never "
                f"{target_type!r} {target_id!r}"
            )

        if target_type == "CLAIM" and target_id not in claim_ids:
            raise DaaleValidationError(
                f"{kernel_id}: Finding {finding['finding_id']} targets unknown claim: {target_id}"
            )
        if target_type == "REQUIREMENT" and target_id not in requirement_ids:
            raise DaaleValidationError(
                f"{kernel_id}: Finding {finding['finding_id']} targets unknown requirement: {target_id}"
            )
        if target_type == "EVIDENCE" and target_id not in evidence_ids:
            raise DaaleValidationError(
                f"{kernel_id}: Finding {finding['finding_id']} targets unknown evidence: {target_id}"
            )
        if target_type not in ("CLAIM", "REQUIREMENT", "EVIDENCE", "POLICY", "GENERAL"):
            raise DaaleValidationError(
                f"{kernel_id}: Finding {finding['finding_id']} has invalid target_type: {target_type}"
            )

        unknown_evidence = set(finding["evidence_ids"]) - evidence_ids
        if unknown_evidence:
            raise DaaleValidationError(
                f"{kernel_id}: Finding {finding['finding_id']} cites unknown evidence: {sorted(unknown_evidence)}"
            )

        if finding["severity"] not in SEVERITIES:
            raise DaaleValidationError(
                f"{kernel_id}: Finding {finding['finding_id']} has invalid severity: {finding['severity']}"
            )

        confidence = finding["confidence"]
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            raise DaaleValidationError(
                f"{kernel_id}: Finding {finding['finding_id']} confidence must be in [0, 1]"
            )

        verdict_rule = _VERDICT_FIELD_BY_FINDING_TYPE.get(finding["finding_type"])
        if verdict_rule is not None:
            field_name, vocabulary = verdict_rule
            verdict = finding.get(field_name)
            if verdict not in vocabulary:
                raise DaaleValidationError(
                    f"{kernel_id}: {finding['finding_type']} finding "
                    f"{finding['finding_id']} must set '{field_name}' to one "
                    f"of {vocabulary}, the verdict the policy engine reads "
                    f"directly -- 'content' is rationale text, never the "
                    f"verdict itself. Received: {verdict!r}"
                )

    # The evidence-relation matrix (every claim classifies every evidence item
    # exactly once) is mandatory for base kernels. The adversary only produces
    # CHALLENGE and CONTRADICTION findings, so we skip this check for it.
    if kernel_id != "ADVERSARY":
        for claim_id in claim_ids:
            claim_relations = [
                f for f in kernel_output["findings"]
                if f["finding_type"] == "EVIDENCE_RELATION" and f["target_id"] == claim_id
            ]
            related_evidence = set()
            for rel in claim_relations:
                if len(rel["evidence_ids"]) != 1:
                    raise DaaleValidationError(
                        f"{kernel_id}: EVIDENCE_RELATION finding {rel['finding_id']} must have exactly one evidence_id"
                    )
                related_evidence.add(rel["evidence_ids"][0])
            if related_evidence != evidence_ids:
                missing = evidence_ids - related_evidence
                extra = related_evidence - evidence_ids
                details = []
                if missing:
                    details.append(f"missing: {sorted(missing)}")
                if extra:
                    details.append(f"extra: {sorted(extra)}")
                raise DaaleValidationError(
                    f"{kernel_id}: Claim {claim_id} must classify every evidence item exactly once. "
                    f"{'; '.join(details)}"
                )
