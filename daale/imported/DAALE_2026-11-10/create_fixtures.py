#!/usr/bin/env python
"""
Generate fixtures for the 3 new court cases: Carlill, Donoghue, Hadley
"""

import json
from pathlib import Path

FIXTURE_DIR = Path(r'D:\DAALE\R-Fabric\fixtures')

# ============================================================
# CARLILL v CARBOLIC SMOKE BALL CO (1893) - Contract Formation
# ============================================================

CARLILL_CASE = {
    "case_id": "CARLILL-1893",
    "decision_stage": "contract_formation_approval",
    "decision_question": "Did the Carbolic Smoke Ball Company's advertisement constitute a binding offer capable of acceptance by performance?",
    "claims": [
        {"claim_id": "C1", "text": "The advertisement constituted a binding unilateral offer."},
        {"claim_id": "C2", "text": "Mrs. Carlill accepted the offer by performing the conditions (using the smoke ball)."},
        {"claim_id": "C3", "text": "The company's deposit of £1000 at the bank demonstrated intention to be bound."},
        {"claim_id": "C4", "text": "No notification of acceptance was required beyond performance."}
    ],
    "evidence": [
        {
            "evidence_id": "E1",
            "text": "Advertisement: '£100 reward will be paid by the Carbolic Smoke Ball Company to any person who contracts the increasing epidemic influenza, colds, or any disease caused by taking cold, after having used the ball three times daily for two weeks according to the printed directions supplied with each ball. £1000 is deposited with the Alliance Bank, Regent Street, showing our sincerity in the matter.'",
            "source": {
                "source_id": "S1",
                "source_type": "DOCUMENT",
                "title": "Carbolic Smoke Ball Advertisement (Pall Mall Gazette, Nov 1891)",
                "collected_at": "1891-11-13T00:00:00Z",
                "document_id": "DOC-ADV-1891-001",
                "source_uri": "file:///evidence/carlill/advertisement.txt",
                "page": 1,
                "section": "Advertisement Text",
                "paragraph": "Full advertisement",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "c1a2b3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
            }
        },
        {
            "evidence_id": "E2",
            "text": "Mrs. Carlill purchased a smoke ball, used it three times daily for two weeks as directed, and contracted influenza.",
            "source": {
                "source_id": "S2",
                "source_type": "DOCUMENT",
                "title": "Witness Statement of Mrs. Louisa Carlill",
                "collected_at": "1892-01-15T00:00:00Z",
                "document_id": "DOC-WIT-1892-002",
                "source_uri": "file:///evidence/carlill/carlill_statement.txt",
                "page": 1,
                "section": "Usage and Illness",
                "paragraph": "Purchase and usage details",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "d2e3f4a5b6c789012345678901234567890abcdef1234567890abcdef1234567"
            }
        },
        {
            "evidence_id": "E3",
            "text": "The company deposited £1000 with the Alliance Bank, Regent Street, as stated in the advertisement.",
            "source": {
                "source_id": "S3",
                "source_type": "SYSTEM_RECORD",
                "title": "Alliance Bank Deposit Record",
                "collected_at": "1891-11-10T00:00:00Z",
                "document_id": "SYS-BANK-1891-003",
                "source_uri": "system://bank-records/alliance/1891-003",
                "page": 1,
                "section": "Deposit Confirmation",
                "paragraph": "Deposit entry",
                "extraction_method": "API",
                "document_version": "1.0",
                "content_hash": "e3f4a5b6c7d89012345678901234567890abcdef1234567890abcdef12345678"
            }
        },
        {
            "evidence_id": "E4",
            "text": "The company argued the advertisement was mere puffery, not a serious offer, and that acceptance required notification.",
            "source": {
                "source_id": "S4",
                "source_type": "DOCUMENT",
                "title": "Defendant's Pleadings (Carbolic Smoke Ball Co.)",
                "collected_at": "1892-06-01T00:00:00Z",
                "document_id": "DOC-PLEAD-1892-004",
                "source_uri": "file:///evidence/carlill/defendant_pleadings.txt",
                "page": 2,
                "section": "Defence Arguments",
                "paragraph": "Puffery and notification requirement",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "f4a5b6c7d8e9012345678901234567890abcdef1234567890abcdef123456789"
            }
        }
    ]
}

# ============================================================
# DONOGHUE v STEVENSON (1932) - Negligence Duty of Care
# ============================================================

DONOGHUE_CASE = {
    "case_id": "DONOGHUE-1932",
    "decision_stage": "negligence_duty_of_care_approval",
    "decision_question": "Does a manufacturer owe a duty of care to the ultimate consumer of a product, absent contractual privity?",
    "claims": [
        {"claim_id": "C1", "text": "The manufacturer (Stevenson) owed a duty of care to the ultimate consumer (Donoghue)."},
        {"claim_id": "C2", "text": "The presence of a decomposed snail in the ginger beer bottle constituted a breach of that duty."},
        {"claim_id": "C3", "text": "The plaintiff's illness was caused by consuming the contaminated product."},
        {"claim_id": "C4", "text": "The absence of contractual privity does not negate the duty of care."}
    ],
    "evidence": [
        {
            "evidence_id": "E1",
            "text": "On 26 August 1928, Mrs. Donoghue consumed ginger beer from an opaque bottle purchased by her friend at the Wellmeadow Café, Paisley. The bottle was manufactured by David Stevenson, Glen Lane, Paisley.",
            "source": {
                "source_id": "S1",
                "source_type": "DOCUMENT",
                "title": "Statement of Facts (Donoghue v Stevenson [1932] AC 562)",
                "collected_at": "1928-08-26T00:00:00Z",
                "document_id": "DOC-FACTS-1928-001",
                "source_uri": "file:///evidence/donoghue/statement_of_facts.txt",
                "page": 1,
                "section": "Purchase and Consumption",
                "paragraph": "Purchase and consumption details",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
            }
        },
        {
            "evidence_id": "E2",
            "text": "After pouring part of the ginger beer, the remainder was poured out and a decomposed snail emerged from the bottle.",
            "source": {
                "source_id": "S2",
                "source_type": "DOCUMENT",
                "title": "Witness Testimony - Mrs. Donoghue and Friend",
                "collected_at": "1928-08-26T00:00:00Z",
                "document_id": "DOC-WIT-1928-002",
                "source_uri": "file:///evidence/donoghue/snail_emergence.txt",
                "page": 1,
                "section": "Contamination Discovery",
                "paragraph": "Snail emergence observation",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3"
            }
        },
        {
            "evidence_id": "E3",
            "text": "Mrs. Donoghue suffered shock and severe gastroenteritis as a result of consuming the contaminated ginger beer.",
            "source": {
                "source_id": "S3",
                "source_type": "DOCUMENT",
                "title": "Medical Report - Dr. McCallum",
                "collected_at": "1928-08-27T00:00:00Z",
                "document_id": "DOC-MED-1928-003",
                "source_uri": "file:///evidence/donoghue/medical_report.txt",
                "page": 1,
                "section": "Diagnosis",
                "paragraph": "Shock and gastroenteritis diagnosis",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4"
            }
        },
        {
            "evidence_id": "E4",
            "text": "There was no contractual relationship between Mrs. Donoghue and Mr. Stevenson; the bottle was purchased by her friend.",
            "source": {
                "source_id": "S4",
                "source_type": "DOCUMENT",
                "title": "Pleadings - Absence of Privity",
                "collected_at": "1930-01-15T00:00:00Z",
                "document_id": "DOC-PLEAD-1930-004",
                "source_uri": "file:///evidence/donoghue/privity_pleadings.txt",
                "page": 1,
                "section": "Contractual Privity",
                "paragraph": "No contract between plaintiff and defendant",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5"
            }
        },
        {
            "evidence_id": "E5",
            "text": "The ginger beer was manufactured by Stevenson and sealed in an opaque bottle, preventing inspection by the consumer or retailer.",
            "source": {
                "source_id": "S5",
                "source_type": "DOCUMENT",
                "title": "Manufacturing Process Evidence",
                "collected_at": "1930-02-01T00:00:00Z",
                "document_id": "DOC-MFG-1930-005",
                "source_uri": "file:///evidence/donoghue/manufacturing.txt",
                "page": 1,
                "section": "Bottling Process",
                "paragraph": "Opaque bottle prevents inspection",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6"
            }
        },
        {
            "evidence_id": "E6",
            "text": "Lord Atkin's 'neighbour principle': 'You must take reasonable care to avoid acts or omissions which you can reasonably foresee would be likely to injure your neighbour.'",
            "source": {
                "source_id": "S6",
                "source_type": "DOCUMENT",
                "title": "House of Lords Judgment (Lord Atkin)",
                "collected_at": "1932-05-26T00:00:00Z",
                "document_id": "DOC-JUD-1932-006",
                "source_uri": "file:///evidence/donoghue/lordatkin_judgment.txt",
                "page": 3,
                "section": "Neighbour Principle",
                "paragraph": "Foundational duty of care formulation",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7"
            }
        }
    ]
}

# ============================================================
# HADLEY v BAXENDALE (1854) - Contract Damages Remoteness
# ============================================================

HADLEY_CASE = {
    "case_id": "HADLEY-1854",
    "decision_stage": "contract_damages_remoteness_approval",
    "decision_question": "Are damages for lost profits recoverable when the carrier did not know the mill was stopped and the special circumstances were not communicated?",
    "claims": [
        {"claim_id": "C1", "text": "The carrier (Baxendale) breached the contract by delaying delivery of the crankshaft."},
        {"claim_id": "C2", "text": "The mill owners (Hadley) lost profits due to the mill being stopped during the delay."},
        {"claim_id": "C3", "text": "The lost profits are recoverable as damages for breach of contract."},
        {"claim_id": "C4", "text": "The carrier knew or should have known that delay would cause lost profits."}
    ],
    "evidence": [
        {
            "evidence_id": "E1",
            "text": "The plaintiff's mill at Gloucester stopped work because the crankshaft of the steam engine broke. The broken crankshaft was sent to the defendant (Baxendale) at Pickford & Co. on 14 May 1853 for delivery to the engineers at Greenwich.",
            "source": {
                "source_id": "S1",
                "source_type": "DOCUMENT",
                "title": "Statement of Facts (Hadley v Baxendale (1854) 9 Ex 341)",
                "collected_at": "1853-05-14T00:00:00Z",
                "document_id": "DOC-FACTS-1853-001",
                "source_uri": "file:///evidence/hadley/statement_of_facts.txt",
                "page": 1,
                "section": "Background and Shipment",
                "paragraph": "Crankshaft shipment details",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
            }
        },
        {
            "evidence_id": "E2",
            "text": "The defendant's clerk was told the crankshaft must be sent immediately. The plaintiff's clerk said the mill was stopped and the shaft must be sent directly. The defendant's clerk replied 'I will send it directly.'",
            "source": {
                "source_id": "S2",
                "source_type": "DOCUMENT",
                "title": "Trial Testimony - Plaintiff's Clerk",
                "collected_at": "1854-02-15T00:00:00Z",
                "document_id": "DOC-WIT-1854-002",
                "source_uri": "file:///evidence/hadley/clerk_testimony.txt",
                "page": 1,
                "section": "Communication at Pickford",
                "paragraph": "Urgency communicated but not special circumstances",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3"
            }
        },
        {
            "evidence_id": "E3",
            "text": "The defendant did not know the mill was stopped; they believed the plaintiff had other engines or could work around the delay. The shaft was not delivered until 19 May (5 days late).",
            "source": {
                "source_id": "S3",
                "source_type": "DOCUMENT",
                "title": "Defendant's Evidence - Pickford & Co. Internal Records",
                "collected_at": "1853-05-19T00:00:00Z",
                "document_id": "DOC-DEF-1853-003",
                "source_uri": "file:///evidence/hadley/delivery_records.txt",
                "page": 1,
                "section": "Delivery Timeline",
                "paragraph": "Late delivery, no knowledge of mill stoppage",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4"
            }
        },
        {
            "evidence_id": "E4",
            "text": "The mill remained stopped from 14 May to 19 May (5 days). The plaintiff claimed lost profits of £300 for the 5-day stoppage.",
            "source": {
                "source_id": "S4",
                "source_type": "DOCUMENT",
                "title": "Plaintiff's Claim for Lost Profits",
                "collected_at": "1854-03-01T00:00:00Z",
                "document_id": "DOC-CLAIM-1854-004",
                "source_uri": "file:///evidence/hadley/lost_profits_claim.txt",
                "page": 1,
                "section": "Damages Calculation",
                "paragraph": "£300 lost profits over 5 days",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5"
            }
        },
        {
            "evidence_id": "E5",
            "text": "The jury awarded £25 damages (reflecting only direct costs). The Court of Exchequer Chamber reversed and held that damages must be such as may fairly and reasonably be considered either arising naturally from the breach, or such as may reasonably be supposed to have been in the contemplation of both parties at the time they made the contract.",
            "source": {
                "source_id": "S5",
                "source_type": "DOCUMENT",
                "title": "Judgment - Court of Exchequer Chamber (Alderson B.)",
                "collected_at": "1854-07-15T00:00:00Z",
                "document_id": "DOC-JUD-1854-005",
                "source_uri": "file:///evidence/hadley/judgment.txt",
                "page": 2,
                "section": "Remoteness Rule Formulation",
                "paragraph": "Hadley rule: arising naturally or in contemplation of parties",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6"
            }
        },
        {
            "evidence_id": "E6",
            "text": "The special circumstances (mill stopped, no other shaft) were not communicated to the carrier. The carrier only knew a shaft was needed for a mill.",
            "source": {
                "source_id": "S6",
                "source_type": "DOCUMENT",
                "title": "Appellate Findings - Communication of Special Circumstances",
                "collected_at": "1854-07-15T00:00:00Z",
                "document_id": "DOC-APP-1854-006",
                "source_uri": "file:///evidence/hadley/special_circumstances.txt",
                "page": 1,
                "section": "Knowledge of Special Circumstances",
                "paragraph": "Carrier unaware mill was stopped",
                "extraction_method": "MANUAL",
                "document_version": "1.0",
                "content_hash": "f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7"
            }
        }
    ]
}

# Helper function to create kernel findings for a case
def create_kernel_fixtures(case_data, policy_data):
    """Generate fixture outputs for all 7 kernels based on case and policy"""
    # This is a template - actual findings would be hand-crafted per case
    pass

if __name__ == '__main__':
    # Write case files
    cases_dir = Path(r'D:\DAALE\R-Fabric\cases')
    
    with open(cases_dir / 'carlill_v_carbolic.json', 'w') as f:
        json.dump(CARLILL_CASE, f, indent=2)
    print("Created carlill_v_carbolic.json")
    
    with open(cases_dir / 'donoghue_v_stevenson.json', 'w') as f:
        json.dump(DONOGHUE_CASE, f, indent=2)
    print("Created donoghue_v_stevenson.json")
    
    with open(cases_dir / 'hadley_v_baxendale.json', 'w') as f:
        json.dump(HADLEY_CASE, f, indent=2)
    print("Created hadley_v_baxendale.json")
    
    print("Case files created successfully!")