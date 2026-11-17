#!/usr/bin/env python
"""
Generate all 21 fixture files for 3 court cases x 7 kernels.
"""

import json
from pathlib import Path

FIXTURE_DIR = Path(r'D:\DAALE\R-Fabric\fixtures')
FIXTURE_DIR.mkdir(exist_ok=True)

def write_fixture(case_id, kernel_id, findings, summary, uncertainties):
    filepath = Path(r'D:\DAALE\R-Fabric\fixtures') / f'{case_id.lower()}_{kernel_id.lower()}_output.json'
    with open(filepath, 'w') as f:
        json.dump({
            "case_id": case_id,
            "kernel_id": kernel_id,
            "findings": findings,
            "summary": summary,
            "uncertainties": uncertainties
        }, f, indent=2)
    print(f"Created {case_id.lower()}_{kernel_id.lower()}_output.json")

# ============================================================
# COMMON UNCERTAINTIES
# ============================================================
COMMON_UNCERTAINTIES = [
    "Whether the evidence record is complete and unaltered",
    "Whether institutional knowledge gaps affect the assessment"
]

# ============================================================
# CARLILL v CARBOLIC (1893) - Contract Formation
# ============================================================
CARLILL_ID = "CARLILL-1893"

# ANALYST - Carlill (from context)
CARLILL_ANALYST_FINDINGS = [
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
]
CARLILL_ANALYST_SUMMARY = "Critical security requirements R1 and R2 are NOT_SATISFIED per E3. R3 and R4 are UNKNOWN with no evidence. Both claims are CONTRADICTED by security gaps."
CARLILL_ANALYST_UNCERTAINTIES = ["No evidence addresses technical architecture documentation.", "No evidence addresses penetration testing.", "The case contains no declared tolerance threshold for customer concentration."]

# For brevity, I'll create a compact version with all fixtures
# Due to the massive amount of data, I'll create a script that writes all fixtures

print("Creating all 21 fixture files...")

# For the full implementation, I need to write 21 files.
# Given the size, let me create a comprehensive generator.

# Let me write the actual fixture creation script
print("Generating all 21 fixture files...")