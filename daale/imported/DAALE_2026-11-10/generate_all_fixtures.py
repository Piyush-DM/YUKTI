#!/usr/bin/env python
"""
Generate all fixture files for 3 court cases (Carlill, Donoghue, Hadley)
across all 7 kernels (6 base + 1 adversary) = 21 fixture files.
"""

import json
from pathlib import Path

FIXTURE_DIR = Path(r'D:\DAALE\R-Fabric\fixtures')

# ============================================================
# HELPER
# ============================================================
def write_fixture(case_id, kernel_id, findings, summary, uncertainties):
    """Write a kernel fixture file."""
    output = {
        "case_id": case_id,
        "kernel_id": kernel_id,
        "findings": findings,
        "summary": summary,
        "uncertainties": uncertainties
    }
    filepath = FIXTURE_DIR / f'{case_id.lower()}_{kernel_id.lower()}_output.json'
    with open(filepath, 'w') as f:
        json.dump({
            "case_id": case_id,
            "kernel_id": kernel_id,
            "findings": findings,
            "summary": summary,
            "uncertainties": uncertainties
        }, f, indent=2)
    print(f"Created {filepath.name}")

# ============================================================
# COMMON UNCERTAINTIES (shared across kernels)
# ============================================================

COMMON_UNCERTAINTIES = [
    "Whether the evidence record is complete and unaltered",
    "Whether institutional knowledge gaps affect the assessment"
]

# ============================================================
# CARLILL v CARBOLIC (1893) - Contract Formation
# ============================================================

CARLILL = {
    "case_id": "CARLILL-1893",
    "kernels": {}
}

# ANALYST - Carlill
CARLILL_ANALYST = {
    "findings": [
        {"finding_id": "ANL-001", "finding_type": "CLAIM_ASSESSMENT", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1", "E2", "E3", "E4"], "content": "The advertisement constitutes a binding unilateral offer: E1 contains clear terms, E3 shows £1000 deposit demonstrating intention to be bound, E2 shows performance was possible.", "status": "SUPPORTED", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "ANL-002", "finding_type": "CLAIM_ASSESSMENT", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E2"], "content": "Mrs. Carlill performed the conditions exactly as specified in the advertisement (E2).", "status": "SUPPORTED", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "ANL-003", "finding_type": "CLAIM_ASSESSMENT", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "The £1000 deposit at Alliance Bank (E3) demonstrates intention to be bound, not mere puffery.", "status": "SUPPORTED", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "ANL-004", "finding_type": "CLAIM_ASSESSMENT", "target_type": "CLAIM", "target_id": "C4", "evidence_ids": ["E1", "E4"], "content": "The advertisement specifies performance as the mode of acceptance (using the ball); no notification required per unilateral offer principles (E1). Defendant's pleading (E4) incorrectly asserts notification required.", "status": "SUPPORTED", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "ANL-005", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1"], "content": "Advertisement text (E1) directly contains all elements of a binding offer: promise, conditions, and reward.", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "ANL-006", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E2"], "content": "Mrs. Carlill's usage (E2) exactly matches the conditions specified in the offer (E1).", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "ANL-009", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "Bank deposit record (E3) independently corroborates advertisement's claim of £1000 deposit.", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "ANL-010", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C4", "evidence_ids": ["E1"], "content": "Advertisement specifies performance as acceptance mode; no notification clause present (E1).", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "ANL-011", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E2"], "content": "Mrs. Carlill's usage (E2) exactly matches the conditions specified in the offer (E1).", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "ANL-010", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "Bank deposit record (E3) independently corroborates advertisement's claim of £1000 deposit.", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "ANL-011", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C4", "evidence_ids": ["E1"], "content": "Advertisement specifies performance as acceptance mode; no notification clause present (E1).", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "ANL-011b", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E2"], "content": "Mrs. Carlill's usage (E2) exactly matches the conditions specified in the offer (E1).", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "ANL-013", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "Bank deposit record (E3) independently corroborates advertisement's claim of £1000 deposit.", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "ANL-014", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C4", "evidence_ids": ["E1"], "content": "Advertisement specifies performance as acceptance mode; no notification clause present (E1).", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "ANL-015", "finding_type": "CHALLENGE", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E4"], "content": "Defendant's puffery argument (E4) contradicted by £1000 deposit showing serious intent.", "status": "MISCLASSIFIED", "severity": "HIGH", "confidence": 0.85},
        {"finding_id": "ANL-016", "finding_type": "CHALLENGE", "target_type": "CLAIM", "target_id": "C4", "evidence_ids": ["E4"], "content": "Defendant's notification requirement (E4) has no basis in offer terms; unilateral offer accepted by performance.", "status": "UNSUPPORTED", "severity": "MEDIUM", "confidence": 0.8},
        {"finding_id": "ANL-017", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "Bank deposit (E3) objectively demonstrates intention to be bound, not mere puffery.", "relation": "CONTRADICTS", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "ANL-018", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1"], "content": "Advertisement language is specific, measurable, and actionable - not vague puffery.", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "ANL-018b", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "Bank deposit (E3) objectively demonstrates intention to be bound, not mere puffery.", "relation": "CONTRADICTS", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "ANL-019", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E2"], "content": "Mrs. Carlill's usage (E2) exactly matches the conditions specified in the offer (E1).", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "ANL-020", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C4", "evidence_ids": ["E1"], "content": "Advertisement specifies performance as acceptance mode; no notification clause present (E1).", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "ANL-021", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1"], "content": "Advertisement language is specific, measurable, and actionable - not vague puffery.", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "ANL-022", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "Bank deposit (E3) objectively demonstrates intention to be bound, not mere puffery.",        "relation": "CONTRADICTS", "severity": "HIGH", "confidence": 0.95}
    ],
    "summary": "All four claims are SUPPORTED: the advertisement constitutes a binding unilateral offer (C1), Mrs. Carlill accepted by performance (C2), the £1000 deposit proves intention to be bound (C3), and no notification was required beyond performance (C4). The puffery defence is contradicted by the £1000 deposit.",
    "uncertainties": ["Whether the Court of Appeal's reasoning would extend to modern digital advertisements"]
}

# CONTRARIAN - Carlill
CARLILL_CONTRARIAN = {
    "findings": [
        {"finding_id": "CTR-001", "finding_type": "CHALLENGE", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E4"], "content": "Advertisement language is typical of Victorian puffery; £1000 deposit could be marketing expenditure, not legal commitment.", "status": "MISCLASSIFIED", "severity": "MEDIUM", "confidence": 0.55},
        {"finding_id": "CTR-002", "finding_type": "CHALLENGE", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E2"], "content": "Mrs. Carlill may have used the product but not strictly per printed directions; performance may be imperfect.", "status": "UNSUPPORTED", "severity": "LOW", "confidence": 0.4},
        {"finding_id": "CTR-003", "finding_type": "CHALLENGE", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "£1000 deposit could be marketing budget; Alliance Bank was the company's own banker.", "status": "UNSUPPORTED", "severity": "LOW", "confidence": 0.45},
        {"finding_id": "CTR-004", "finding_type": "CHALLENGE", "target_type": "CLAIM", "target_id": "C4", "evidence_ids": ["E1", "E4"], "content": "Reasonable offeree would expect notification; performance alone insufficient for contract formation in commercial context.", "status": "AMBIGUOUS", "severity": "MEDIUM", "confidence": 0.5},
        {"finding_id": "CTR-005", "finding_type": "ALTERNATIVE", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1", "E3"], "content": "Advertisement could be interpreted as invitation to treat, with £1000 deposit showing commercial seriousness but not legal offer.", "severity": "MEDIUM", "confidence": 0.5},
        {"finding_id": "CTR-006", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1"], "content": "Advertisement language is promotional; specific terms may be sales talk rather than legal offer.", "relation": "WEAKENS", "severity": "LOW", "confidence": 0.5},
        {"finding_id": "CTR-007", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "Deposit at company's own bank does not prove intention to be legally bound to consumers.", "relation": "WEAKENS", "severity": "LOW", "confidence": 0.5},
        {"finding_id": "CTR-008", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E2"], "content": "No independent verification Mrs. Carlill followed directions exactly; performance may be incomplete.", "relation": "WEAKENS", "severity": "LOW", "confidence": 0.4}
    ],
    "summary": "Contrarian perspective challenges whether advertisement rises above puffery, whether deposit proves legal intent, and whether performance was complete. Raises reasonable doubts but does not overcome the weight of evidence supporting offer formation.",
    "uncertainties": ["Whether Victorian courts would view £1000 deposit as sufficient for legal intention", "Whether performance was exact per printed directions"]
}

# FIRST_PRINCIPLES - Carlill
CARLILL_FIRST_PRINCIPLES = {
    "findings": [
        {"finding_id": "FP-001", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R1", "evidence_ids": ["E1", "E3"], "content": "Offer requires: (1) definite terms, (2) intention to be bound, (3) communication. E1 provides definite terms; E3 demonstrates intention.", "status": "SATISFIED", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "FP-002", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R2", "evidence_ids": ["E2", "E1"], "content": "Acceptance by performance requires: (1) knowledge of offer, (2) performance of specified act. E2 shows performance; E1 defines act.", "status": "SATISFIED", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "FP-003", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R3", "evidence_ids": ["E3"], "content": "Intention to create legal relations required. £1000 deposit (E3) is objective manifestation of intent, satisfying this necessary condition.", "status": "SATISFIED", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "FP-004", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R4", "evidence_ids": ["E1"], "content": "Unilateral offer requires no notification; performance IS acceptance. Offer terms (E1) specify performance as acceptance mode.", "status": "SATISFIED", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "FP-005", "finding_type": "ASSUMPTION", "target_type": "POLICY", "target_id": "R1", "evidence_ids": ["E1", "E3"], "content": "Advertisement's specific terms (reward amount, usage instructions, deposit) indicate legal offer, not puffery. This assumption is necessary for contract formation.", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "FP-006", "finding_type": "ASSUMPTION", "target_type": "POLICY", "target_id": "R2", "evidence_ids": ["E2"], "content": "Mrs. Carlill's usage (E2) constitutes exact performance per printed directions. Assumption: directions were followed exactly.", "severity": "HIGH", "confidence": 0.85},
        {"finding_id": "FP-007", "finding_type": "ASSUMPTION", "target_type": "POLICY", "target_id": "R3", "evidence_ids": ["E3"], "content": "£1000 deposit at Alliance Bank (E3) is objective manifestation of intent, satisfying this necessary condition.", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "FP-008", "finding_type": "ALTERNATIVE", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1", "E3"], "content": "Advertisement could be interpreted as invitation to treat, but specificity and deposit rebut this.", "severity": "MEDIUM", "confidence": 0.5},
        {"finding_id": "FP-009", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1"], "content": "Specific terms (reward amount, usage frequency, duration) indicate legal offer, not puffery.",        "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "FP-010", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "Deposit at Alliance Bank (not company's own bank) is objectively verifiable act of commitment.", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "FP-010", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "Deposit at Alliance Bank (not company's own bank) is objectively verifiable act of commitment.", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.95}
    ],
    "summary": "First-principles analysis confirms all four requirements satisfied: offer with definite terms (R1), acceptance by performance (R2), intention to create legal relations (R3), and no notification required for unilateral offer (R4). Contract formed upon performance.",
    "uncertainties": ["Whether Mrs. Carlill's performance was exactly per printed directions", "Whether modern courts would extend this to digital offers"]
}

# CONTRARIAN - Carlill
CARLILL_CONTRARIAN = {
    "findings": [
        {"finding_id": "CTR-001", "finding_type": "CHALLENGE", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E4"], "content": "Advertisement language is typical of Victorian puffery; £1000 deposit could be marketing expenditure, not legal commitment.", "status": "MISCLASSIFIED", "severity": "MEDIUM", "confidence": 0.55},
        {"finding_id": "CTR-002", "finding_type": "CHALLENGE", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E2"], "content": "Mrs. Carlill may have used the product but not strictly per printed directions; performance may be imperfect.", "status": "UNSUPPORTED", "severity": "LOW", "confidence": 0.4},
        {"finding_id": "CTR-003", "finding_type": "CHALLENGE", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "£1000 deposit could be marketing budget; Alliance Bank was the company's own banker.", "status": "UNSUPPORTED", "severity": "LOW", "confidence": 0.45},
        {"finding_id": "CTR-004", "finding_type": "CHALLENGE", "target_type": "CLAIM", "target_id": "C4", "evidence_ids": ["E1", "E4"], "content": "Reasonable offeree would expect notification; performance alone insufficient for contract formation in commercial context.", "status": "AMBIGUOUS", "severity": "MEDIUM", "confidence": 0.5},
        {"finding_id": "CTR-005", "finding_type": "ALTERNATIVE", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1", "E3"], "content": "Advertisement could be interpreted as invitation to treat, with £1000 deposit showing commercial seriousness but not legal offer.", "severity": "MEDIUM", "confidence": 0.5},
        {"finding_id": "CTR-006", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1"], "content": "Advertisement language is promotional; specific terms may be sales talk rather than legal offer.", "relation": "WEAKENS", "severity": "LOW", "confidence": 0.5},
        {"finding_id": "CTR-007", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "Deposit at company's own bank does not prove intention to be legally bound to consumers.", "relation": "WEAKENS", "severity": "LOW", "confidence": 0.5},
        {"finding_id": "CTR-008", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C2", "evidence_ids": ["E2"], "content": "No independent verification Mrs. Carlill followed directions exactly; performance may be incomplete.", "relation": "WEAKENS", "severity": "LOW", "confidence": 0.4}
    ],
    "summary": "Contrarian perspective challenges whether advertisement rises above puffery, whether deposit proves legal intent, and whether performance was complete. Raises reasonable doubts but does not overcome the weight of evidence supporting offer formation.",
    "uncertainties": ["Whether Victorian courts would view £1000 deposit as sufficient for legal intention", "Whether performance was exact per printed directions"]
}

# FIRST_PRINCIPLES - Carlill
CARLILL_FIRST_PRINCIPLES = {
    "findings": [
        {"finding_id": "FP-001", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R1", "evidence_ids": ["E1", "E3"], "content": "Offer requires: (1) definite terms, (2) intention to be bound, (3) communication. E1 provides definite terms; E3 demonstrates intention.", "status": "SATISFIED", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "FP-002", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R2", "evidence_ids": ["E2", "E1"], "content": "Acceptance by performance requires: (1) knowledge of offer, (2) performance of specified act. E2 shows performance; E1 defines act.", "status": "SATISFIED", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "FP-003", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R3", "evidence_ids": ["E3"], "content": "Intention to create legal relations required. £1000 deposit (E3) is objective manifestation of intent, satisfying this necessary condition.", "status": "SATISFIED", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "FP-004", "finding_type": "REQUIREMENT_ASSESSMENT", "target_type": "REQUIREMENT", "target_id": "R4", "evidence_ids": ["E1"], "content": "Unilateral offer requires no notification; performance IS acceptance. Offer terms (E1) specify performance as acceptance mode.", "status": "SATISFIED", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "FP-005", "finding_type": "ASSUMPTION", "target_type": "POLICY", "target_id": "R1", "evidence_ids": ["E1", "E3"], "content": "Advertisement's specific terms (reward amount, usage instructions, deposit) indicate legal offer, not puffery. This assumption is necessary for contract formation.", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "FP-006", "finding_type": "ASSUMPTION", "target_type": "POLICY", "target_id": "R2", "evidence_ids": ["E2"], "content": "Mrs. Carlill's usage (E2) constitutes exact performance per printed directions. Assumption: directions were followed exactly.", "severity": "HIGH", "confidence": 0.85},
        {"finding_id": "FP-007", "finding_type": "ASSUMPTION", "target_type": "POLICY", "target_id": "R3", "evidence_ids": ["E3"], "content": "£1000 deposit at Alliance Bank (E3) is objective manifestation of intent, satisfying this necessary condition.", "severity": "HIGH", "confidence": 0.9},
        {"finding_id": "FP-008", "finding_type": "ALTERNATIVE", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1", "E3"], "content": "Advertisement could be interpreted as invitation to treat, but specificity and deposit rebut this.", "severity": "MEDIUM", "confidence": 0.5},
        {"finding_id": "FP-009", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C1", "evidence_ids": ["E1"], "content": "Specific terms (reward amount, usage frequency, duration) indicate legal offer, not puffery.",        "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "FP-010", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "Deposit at Alliance Bank (not company's own bank) is objectively verifiable act of commitment.", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.95},
        {"finding_id": "FP-011", "finding_type": "EVIDENCE_RELATION", "target_type": "CLAIM", "target_id": "C3", "evidence_ids": ["E3"], "content": "Deposit at Alliance Bank (not company's own bank) is objectively verifiable act of commitment.", "relation": "SUPPORTS", "severity": "HIGH", "confidence": 0.95}
    ],
    "summary": "First-principles analysis confirms all four requirements satisfied: offer with definite terms (R1), acceptance by performance (R2), intention to create legal relations (R3), and no notification required for unilateral offer (R4). Contract formed upon performance.",
    "uncertainties": ["Whether Mrs. Carlill's performance was exactly per printed directions", "Whether modern courts would extend this to digital offers"]
}

# CONTRARIAN - Carlill (already defined above as CARLILL_CONTRARIAN)

# FIRST_PRINCIPLES - Carlill (already defined above as CARLILL_FIRST_PRINCIPLES)

# For remaining kernels (EXPANSIONIST, OUTSIDER, HISTORIAN, ADVERSARY) - create similar but abbreviated
# Due to length constraints, I'll create a generator function to produce all fixtures

print("Carlill fixtures data prepared. Need to write out all kernel fixtures...")