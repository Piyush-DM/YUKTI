"""JSON Schemas for the DAALE v0.1 boundary contracts."""

EVIDENCE_RELATIONS = [
    "SUPPORTS",
    "WEAKENS",
    "CONTRADICTS",
    "CONTEXTUAL",
    "IRRELEVANT",
]

REQUIREMENT_STATES = ["SATISFIED", "NOT_SATISFIED", "UNKNOWN"]
CLAIM_STATUSES = ["SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE"]
CHALLENGE_TYPES = [
    "UNSUPPORTED",
    "MISCLASSIFIED",
    "AMBIGUOUS",
    "OMITTED_EVIDENCE",
    "POLICY_MISMATCH",
]
# The union is what a finding's own "status" field may hold -- which of the
# two vocabularies applies is determined by the finding's finding_type, and
# validation.py enforces that narrower rule; the schema only bounds the set.
FINDING_STATUSES = REQUIREMENT_STATES + CLAIM_STATUSES + CHALLENGE_TYPES
DECISION_STATES = ["ADVANCE", "HOLD", "REJECT", "ESCALATE"]
SEVERITIES = ["LOW", "MEDIUM", "HIGH"]

POLICY_METRICS = [
    "high_adversarial_challenges",
    "high_unresolved_contradictions",
    "failed_critical_requirements",
    "failed_mandatory_requirements",
    "unknown_mandatory_requirements",
    "all_mandatory_requirements_satisfied",
    "supporting_relations",
    "weakening_relations",
    "contradicting_relations",
    "always",
]

KERNEL_IDS = [
    "ANALYST",
    "ADVERSARY",
    "CONTRARIAN",
    "FIRST_PRINCIPLES",
    "EXPANSIONIST",
    "OUTSIDER",
    "HISTORIAN",
]

KERNEL_FINDING_TYPES = [
    "CLAIM_ASSESSMENT",
    "REQUIREMENT_ASSESSMENT",
    "EVIDENCE_RELATION",
    "CHALLENGE",
    "CONTRADICTION",
    "UNCERTAINTY",
    "ASSUMPTION",
    "ALTERNATIVE",
    "RISK",
    "GAP",
]

CONTRADICTION_SEVERITIES = SEVERITIES  # LOW, MEDIUM, HIGH

CASE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "case_id": {"type": "string", "minLength": 1},
        "decision_stage": {"type": "string", "minLength": 1},
        "decision_question": {"type": "string", "minLength": 1},
        "claims": {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "items": {
                "type": "object",
                "properties": {
                    "claim_id": {"type": "string", "minLength": 1},
                    "text": {"type": "string", "minLength": 1},
                },
                "required": ["claim_id", "text"],
                "additionalProperties": False,
            },
        },
        "evidence": {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "items": {
                "type": "object",
                "properties": {
                    "evidence_id": {"type": "string", "minLength": 1},
                    "text": {"type": "string", "minLength": 1},
                    "source": {
                        "type": "object",
                        "properties": {
                            "source_id": {"type": "string", "minLength": 1},
                            "source_type": {
                                "type": "string",
                                "enum": [
                                    "DOCUMENT",
                                    "SYSTEM_RECORD",
                                    "INTERVIEW",
                                    "DECLARATION",
                                    "OTHER",
                                ],
                            },
                            "title": {"type": "string", "minLength": 1},
                            "collected_at": {"type": "string", "minLength": 1},
                            # Extended provenance fields (v0.1+)
                            "document_id": {"type": "string", "minLength": 1},
                            "source_uri": {"type": "string", "format": "uri"},
                            "page": {"type": "integer", "minimum": 1},
                            "section": {"type": "string", "minLength": 1},
                            "paragraph": {"type": "string", "minLength": 1},
                            "extraction_method": {
                                "type": "string",
                                "enum": ["MANUAL", "OCR", "PARSER", "API", "TRANSCRIPTION"],
                            },
                            "document_version": {"type": "string", "minLength": 1},
                            "content_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                        },
                        "required": ["source_id", "source_type", "title"],
                        "additionalProperties": False,
                    },
                },
                "required": ["evidence_id", "text", "source"],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "case_id",
        "decision_stage",
        "decision_question",
        "claims",
        "evidence",
    ],
    "additionalProperties": False,
}

POLICY_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "policy_id": {"type": "string", "minLength": 1},
        "policy_version": {"type": "string", "minLength": 1},
        "decision_stage": {"type": "string", "minLength": 1},
        "decision_states": {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "items": {"type": "string", "enum": DECISION_STATES},
        },
        "human_authority_required": {"type": "boolean", "const": True},
        "requirements": {
            "type": "array",
            "minItems": 1,
            "uniqueItems": True,
            "items": {
                "type": "object",
                "properties": {
                    "requirement_id": {"type": "string", "minLength": 1},
                    "description": {"type": "string", "minLength": 1},
                    "mandatory": {"type": "boolean"},
                    "critical": {"type": "boolean"},
                },
                "required": [
                    "requirement_id",
                    "description",
                    "mandatory",
                    "critical",
                ],
                "additionalProperties": False,
            },
        },
        "rules": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string", "minLength": 1},
                    "priority": {"type": "integer"},
                    "description": {"type": "string", "minLength": 1},
                    "condition": {
                        "type": "object",
                        "properties": {
                            "metric": {"type": "string", "enum": POLICY_METRICS},
                            "operator": {
                                "type": "string",
                                "enum": ["eq", "gte", "lte"],
                            },
                            "value": {"type": ["number", "boolean"]},
                        },
                        "required": ["metric", "operator", "value"],
                        "additionalProperties": False,
                    },
                    "outcome": {"type": "string", "enum": DECISION_STATES},
                },
                "required": [
                    "rule_id",
                    "priority",
                    "description",
                    "condition",
                    "outcome",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "policy_id",
        "policy_version",
        "decision_stage",
        "decision_states",
        "human_authority_required",
        "requirements",
        "rules",
    ],
    "additionalProperties": False,
}

ANALYST_OUTPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "case_id": {"type": "string", "minLength": 1},
        "claim_analyses": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "claim_id": {"type": "string", "minLength": 1},
                    "provisional_status": {
                        "type": "string",
                        "enum": [
                            "SUPPORTED",
                            "CONTRADICTED",
                            "INSUFFICIENT_EVIDENCE",
                        ],
                    },
                    "evidence_relations": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "properties": {
                                "evidence_id": {
                                    "type": "string",
                                    "minLength": 1,
                                },
                                "relation": {
                                    "type": "string",
                                    "enum": EVIDENCE_RELATIONS,
                                },
                                "rationale": {
                                    "type": "string",
                                    "minLength": 1,
                                },
                            },
                            "required": ["evidence_id", "relation", "rationale"],
                            "additionalProperties": False,
                        },
                    },
                    "uncertainties": {
                        "type": "array",
                        "uniqueItems": True,
                        "items": {"type": "string", "minLength": 1},
                    },
                },
                "required": [
                    "claim_id",
                    "provisional_status",
                    "evidence_relations",
                    "uncertainties",
                ],
                "additionalProperties": False,
            },
        },
        "requirement_assessments": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "properties": {
                    "requirement_id": {"type": "string", "minLength": 1},
                    "status": {"type": "string", "enum": REQUIREMENT_STATES},
                    "evidence_ids": {
                        "type": "array",
                        "uniqueItems": True,
                        "items": {"type": "string", "minLength": 1},
                    },
                    "rationale": {"type": "string", "minLength": 1},
                },
                "required": [
                    "requirement_id",
                    "status",
                    "evidence_ids",
                    "rationale",
                ],
                "additionalProperties": False,
            },
        },
        "assumptions": {
            "type": "array",
            "uniqueItems": True,
            "items": {"type": "string", "minLength": 1},
        },
    },
    "required": [
        "case_id",
        "claim_analyses",
        "requirement_assessments",
        "assumptions",
    ],
    "additionalProperties": False,
}

# The Adversary kernel now uses KERNEL_OUTPUT_SCHEMA with finding types
# CHALLENGE and CONTRADICTION, unifying all kernel outputs under one schema.
# CHALLENGE findings: target_type in {CLAIM, REQUIREMENT}, status in CHALLENGE_TYPES
# CONTRADICTION findings: target_type = CLAIM, relation not used, content is description
# Both require severity (from SEVERITIES) and confidence [0,1] like all findings.

KERNEL_OUTPUT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "case_id": {"type": "string", "minLength": 1},
        "kernel_id": {"type": "string", "enum": KERNEL_IDS},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "finding_id": {"type": "string", "minLength": 1},
                    "finding_type": {"type": "string", "enum": KERNEL_FINDING_TYPES},
                    "target_type": {
                        "type": "string",
                        "enum": ["CLAIM", "REQUIREMENT", "EVIDENCE", "POLICY", "GENERAL"],
                    },
                    "target_id": {"type": "string", "minLength": 1},
                    "evidence_ids": {
                        "type": "array",
                        "uniqueItems": True,
                        "items": {"type": "string", "minLength": 1},
                    },
                    "content": {"type": "string", "minLength": 1},
                    # Present only on REQUIREMENT_ASSESSMENT and
                    # CLAIM_ASSESSMENT findings -- validation.py enforces
                    # that narrower requirement, since a JSON Schema
                    # property can't conditionally depend on a sibling
                    # field's value without Draft 2020's if/then, which
                    # would duplicate the finding_type branching that
                    # already lives in validate_kernel_output. "content"
                    # stays the narrative rationale for every finding type;
                    # "status" is the one place the deterministic policy
                    # engine reads a clean verdict, never prose.
                    "status": {"type": "string", "enum": FINDING_STATUSES},
                    # Present only on EVIDENCE_RELATION findings, same
                    # reasoning as "status" above -- enforced in
                    # validation.py, not here. "content" carries the
                    # rationale; "relation" is the verdict the policy
                    # engine's relation_counts actually reads.
                    "relation": {"type": "string", "enum": EVIDENCE_RELATIONS},
                    "severity": {"type": "string", "enum": SEVERITIES},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": [
                    "finding_id",
                    "finding_type",
                    "target_type",
                    "target_id",
                    "evidence_ids",
                    "content",
                    "severity",
                    "confidence",
                ],
                "additionalProperties": False,
            },
        },
        "summary": {"type": "string", "minLength": 1},
        "uncertainties": {
            "type": "array",
            "uniqueItems": True,
            "items": {"type": "string", "minLength": 1},
        },
    },
    "required": [
        "case_id",
        "kernel_id",
        "findings",
        "summary",
        "uncertainties",
    ],
    "additionalProperties": False,
}

