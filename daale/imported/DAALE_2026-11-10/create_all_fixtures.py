#!/usr/bin/env python
"""
Generate all 21 fixture files for 3 court cases × 7 kernels.
"""

import json
from pathlib import Path

FIXTURE_DIR = Path(r'D:\DAALE\R-Fabric\fixtures')
FIXTURE_DIR.mkdir(exist_ok=True)

# ============================================================
# HELPER
# ============================================================
def write_fixture(case_id, kernel_id, findings, summary, uncertainties):
    filepath = Path(r'D:\DAALE\R-Fabric\fixtures') / f'{case_id.lower()}_{kernel_id.lower()}_output.json'
    with open(Path(r'D:\DAALE\R-Fabric\fixtures') / f'{case_id.lower()}_{kernel_id.lower()}_output.json', 'w') as f:
        json.dump({
            "case_id": case_id,
            "kernel_id": kernel_id,
            "findings": findings,
            "summary": summary,
            "uncertainties": uncertainties
        }, f, indent=2)
    print(f"Created {filepath.name}")

# ============================================================
# CARLILL v CARBOLIC (1893) - Contract Formation
# ============================================================
CARLILL_KERNELS = {
    "ANALYST": {
        "findings": [
            {"finding_id": "ANL-001", "finding_type": "CLAIM_ASSESSMENT", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1", "E2", "E3", "E4"], "content": "The advertisement constitutes a binding unilateral offer: E1 contains clear terms, E3 shows £1000 deposit demonstrating intention to be bound, E2 shows performance was possible.", "status": "SUPPORTED", "severity": "HIGH", "confidence": 0.95},
            {"finding_id": "ANL-002", "finding_type": "CLAIM_ASSESSMENT", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E2"], "content": "Mrs. Carlill performed the conditions exactly as specified in the advertisement (E2).", "status": "SUPPORTED", "severity": "HIGH", "confidence": 0.9},
            {"finding_id": "ANL-003", "finding_type": "CLAIM_ASSESSMENT", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "The £1000 deposit at Alliance Bank (E3) demonstrates intention to be bound, not mere puffery.", "status": "SUPPORTED", "severity": "HIGH", "confidence": 0.95},
            {"finding_id": "ANL-004", "finding_type": "CLAIM_ASSESSMENT", "target_type": "CLAIM", "target_id": "C4", "evidence_ids": ["E1", "E4"], "content": "The advertisement specifies performance as the mode of acceptance (using the ball); no notification required per unilateral offer principles (E1). Defendant's pleading (E4) incorrectly asserts notification required.", "status": "SUPPORTED", "severity": "HIGH", "confidence": 0.9},
            {"finding_id": "ANL-005", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1"], "content": "Advertisement text (E1) directly contains all elements of a binding offer: promise, conditions, and reward.", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.95},
            {"finding_id": "ANL-006", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E2"], "content": "Mrs. Carlill's usage (E2) exactly matches the conditions specified in the offer (E1).", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.9},
            {"finding_id": "ANL-007", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E3"], "content": "Bank deposit record (E3) independently corroborates advertisement's claim of £1000 deposit.", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.95},
            {"finding_id": "ANL-008", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E3"], "content": "An incomplete questionnaire and missing SOC 2 report directly contradict completion of the required controls.", "relation": "CONTRADICTS", "severity": "HIGH", "confidence": 0.95},
            {"finding_id": "ANL-009", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E2"], "content": "Customer concentration has no bearing on completion of security or technical due-diligence controls.", "relation": "IRRELEVANT", "severity": "LOW", "confidence": 0.9},
            {"finding_id": "ANL-010", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1"], "content": "Revenue growth has no bearing on completion of security or technical due-diligence controls.", "relation": "IRRELEVANT", "severity": "LOW", "confidence": 0.9},
            {"finding_id": "ANL-011", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E1"], "content": "Sustained revenue growth is a favorable signal for an acceptable risk profile.", "relation": "SUPPORTS", "severity": "LOW", "confidence": 0.7},
            {"finding_id": "ANL-012", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E2"], "content": "42 percent customer concentration is an unmitigated risk factor that weakens the risk-profile claim.", "relation": "WEAKENS", "severity": "MEDIUM", "confidence": 0.8},
            {"finding_id": "ANL-013", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E3"], "content": "An unresolved security gap directly contradicts a claim of acceptable risk.", "relation": "CONTRADICTS", "severity": "HIGH", "confidence": 0.9},
            {"finding_id": "ANL-014", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R1", "evidence_ids": ["E3"], "content": "E3 explicitly states the security questionnaire is incomplete, which directly establishes non-completion.", "status": "NOT_SATISFIED", "severity": "HIGH", "confidence": 0.95},
            {"finding_id": "ANL-015", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R2", "evidence_ids": ["E3"], "content": "E3 states no SOC 2 report was supplied and does not mention an accepted equivalent assurance.", "status": "NOT_SATISFIED", "severity": "HIGH", "confidence": 0.95},
            {"finding_id": "ANL-016", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R3", "evidence_ids": [], "content": "No supplied evidence addresses technical architecture documentation in either direction.", "status": "UNKNOWN", "severity": "MEDIUM", "confidence": 0.8},
            {"finding_id": "ANL-017", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R4", "evidence_ids": [], "content": "No supplied evidence addresses a penetration-test report in either direction.", "status": "UNKNOWN", "severity": "MEDIUM", "confidence": 0.8},
            {"finding_id": "ANL-018", "finding_type": "UNCERTAINTY", "target_type": "GENERAL", "target_id": "C1", "evidence_ids": [], "content": "No evidence addresses technical architecture documentation.", "severity": "MEDIUM", "confidence": 0.7},
            {"finding_id": "ANL-019", "finding_type": "UNCERTAINTY", "target_type": "GENERAL", "target_id": "C1", "evidence_ids": [], "content": "No evidence addresses penetration testing.", "severity": "MEDIUM", "confidence": 0.7},
            {"finding_id": "ANL-020", "finding_type": "UNCERTAINTY", "target_type": "GENERAL", "target_id": "C2", "evidence_ids": [], "content": "The case contains no declared tolerance threshold for customer concentration.", "severity": "MEDIUM", "confidence": 0.7}
        ],
        "summary": "Critical security requirements R1 and R2 are NOT_SATISFIED per E3. R3 and R4 are UNKNOWN with no evidence. Both claims are CONTRADICTED by security gaps.",
        "uncertainties": ["No evidence addresses technical architecture documentation.", "No evidence addresses penetration testing.", "The case contains no declared tolerance threshold for customer concentration."]
    },
    "CONTRARIAN": {
        "findings": [
            {"finding_id": "CTR-001", "finding_type": "CHALLENGE", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E3"], "content": "The incomplete security questionnaire (E3) does not definitively prove controls were NOT completed; absence of evidence is not evidence of absence.", "status": "MISCLASSIFIED", "severity": "MEDIUM", "confidence": 0.65},
            {"finding_id": "CTR-002", "finding_type": "CHALLENGE", "target_type": "REQUIREMENT", "target_id": "R3", "evidence_ids": ["E1", "E2"], "content": "Revenue growth (E1) and customer concentration (E2) suggest operational maturity that may imply adequate technical architecture even without explicit documentation.",            "status": "UNSUPPORTED", "severity": "LOW", "confidence": 0.4},
            {"finding_id": "CTR-003", "finding_type": "ALTERNATIVE", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E1", "E2"], "content": "Customer concentration risk (E2) may be mitigated by contract terms not visible in evidence; financial viability (E1) could offset technical gaps.", "severity": "MEDIUM", "confidence": 0.5},
            {"finding_id": "CTR-004", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1"], "content": "Revenue growth has no bearing on completion of security or technical due-diligence controls.", "relation": "IRRELEVANT", "severity": "LOW", "confidence": 0.7},
            {"finding_id": "CTR-005", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E2"], "content": "Customer concentration has no bearing on completion of security or technical due-diligence controls.", "relation": "IRRELEVANT", "severity": "LOW", "confidence": 0.7},
            {"finding_id": "CTR-006", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E3"], "content": "An incomplete questionnaire weakens rather than definitively contradicts completion, given the ambiguity of 'incomplete'.", "relation": "WEAKENS", "severity": "MEDIUM", "confidence": 0.65},
            {"finding_id": "CTR-007", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E1"], "content": "Sustained revenue growth supports an acceptable risk profile.", "relation": "SUPPORTS", "severity": "LOW", "confidence": 0.6},
            {"finding_id": "CTR-008", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E2"], "content": "Customer concentration is context for the risk profile without independently resolving it.", "relation": "CONTEXTUAL", "severity": "LOW", "confidence": 0.55},
            {"finding_id": "CTR-009", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E3"], "content": "An unresolved security gap contradicts a claim of acceptable risk.", "relation": "CONTRADICTS", "severity": "HIGH", "confidence": 0.8}
        ],
        "summary": "Contrarian perspective finds plausible alternative interpretations that weaken the NOT_SATISFIED assessments for R1 and R2, and suggests R3/R4 may be satisfied implicitly.",
        "uncertainties": ["Whether E3's 'incomplete' means partially complete or entirely absent", "Whether vendor has undocumented compensating controls"]
    },
    "FIRST_PRINCIPLES": {
        "findings": [
            {"finding_id": "FP-001", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R1", "evidence_ids": ["E3"], "content": "Questionnaire completion is a necessary condition with no substitute; E3 establishes it is not met.", "status": "NOT_SATISFIED", "severity": "HIGH", "confidence": 0.95},
            {"finding_id": "FP-002", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R2", "evidence_ids": ["E3"], "content": "E3 establishes no SOC 2 report was supplied, matching the pattern of NOT_SATISFIED in precedent cases with identical evidence.", "status": "NOT_SATISFIED", "severity": "HIGH", "confidence": 0.95},
            {"finding_id": "FP-003", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R3", "evidence_ids": [], "content": "No evidence addresses this requirement in either direction.", "status": "UNKNOWN", "severity": "MEDIUM", "confidence": 0.8},
            {"finding_id": "FP-004", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R4", "evidence_ids": [], "content": "No evidence addresses this requirement in either direction.", "status": "UNKNOWN", "severity": "MEDIUM", "confidence": 0.8},
            {"finding_id": "FP-005", "finding_type": "ASSUMPTION", "target_type": "POLICY", "target_id": "R1", "evidence_ids": ["E3"], "content": "Questionnaire completion is a necessary condition with no substitute; E3 establishes it is not met.", "severity": "HIGH", "confidence": 0.9},
            {"finding_id": "FP-007", "finding_type": "ASSUMPTION", "target_type": "POLICY", "target_id": "R2", "evidence_ids": ["E3"], "content": "A SOC 2 or equivalent is a necessary condition with no substitute; E3 establishes it is not met.", "severity": "HIGH", "confidence": 0.9},
            {"finding_id": "FP-008", "finding_type": "ASSUMPTION", "target_type": "POLICY", "target_id": "R3", "evidence_ids": [], "content": "No evidence establishes whether this necessary condition is met.", "severity": "MEDIUM", "confidence": 0.8},
            {"finding_id": "FP-008", "finding_type": "ALTERNATIVE", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E1", "E2"], "content": "Customer concentration risk (E2) may be mitigated by contract terms not visible in evidence; financial viability (E1) could offset technical gaps.", "severity": "MEDIUM", "confidence": 0.5},
            {"finding_id": "FP-009", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1"], "content": "Revenue growth has no bearing on completion of security or technical due-diligence controls.", "relation": "IRRELEVANT", "severity": "LOW", "confidence": 0.9},
            {"finding_id": "FP-010", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E2"], "content": "Customer concentration has no bearing on completion of security or technical due-diligence controls.", "relation": "IRRELEVANT", "severity": "LOW", "confidence": 0.9},
            {"finding_id": "FP-011", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E3"], "content": "An incomplete questionnaire and missing SOC 2 report contradict completion of the required controls, and no external reviewer would accept otherwise.", "relation": "CONTRADICTS", "severity": "HIGH", "confidence": 0.95}
        ],
        "summary": "First-principles analysis confirms R1 and R2 are NOT_SATISFIED as necessary conditions with no substitutes. R3 and R4 are UNKNOWN with identified necessary-condition gaps.",
        "uncertainties": ["Whether the policy's 'mandatory' requirements map to necessary conditions or sufficient conditions", "Whether compensating controls could satisfy R3/R4 without direct evidence"]
    }
}

# ============================================================
# CONTRARIAN - Vendor Alpha (already defined in context)
# ============================================================

VENDOR_CONTRARIAN = {
    "findings": [
        {"finding_id": "CTR-001", "finding_type": "CHALLENGE", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E2", "E3"], "content": "The phrase acceptable risk profile combines business concentration risk and technical assurance risk without an application-defined tolerance for customer concentration.", "status": "AMBIGUOUS", "severity": "MEDIUM", "confidence": 0.75},
        {"finding_id": "ADV-001", "finding_type": "CHALLENGE", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E2", "E3"], "content": "The phrase acceptable risk profile combines business concentration risk and technical assurance risk without an application-defined tolerance for customer concentration.", "status": "AMBIGUOUS", "severity": "MEDIUM", "confidence": 0.75}
    ],
    "summary": "The critical security failures are directly grounded in E3. The broader acceptability claim remains partly ambiguous because the policy does not define a customer-concentration threshold.",
    "uncertainties": []
}

# Now I need to create the remaining kernels for Vendor Alpha (CONTRARIAN, FIRST_PRINCIPLES, EXPANSIONIST, OUTSIDER, HISTORIAN, ADVERSARY)
# And all 7 kernels for Donoghue and Hadley cases
# This is a massive amount of data. Let me write a script that creates all fixtures.

print("Data structures prepared. Now writing fixture files...")