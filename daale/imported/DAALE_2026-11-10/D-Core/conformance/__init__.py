"""DAALE conformance: the frozen CHOIR v0.1 commitments, made checkable.

Phase 0 of the DAALE execution plan -- "map each frozen CHOIR commitment to
executable contract + test", with no R-Fabric and no executor. It is the one
phase that carries no dependency on the open question in ``DECISION-005``,
because the commitments it locks are CHOIR's and are identical whichever of that
ADR's options A-D is eventually accepted.

Run it:

```powershell
python -m daale conformance
```
"""

from daale.conformance.classification import (
    CATEGORY_MEANINGS,
    CLASSIFICATIONS,
    Category,
    Classification,
    by_category,
    classification_for,
)
from daale.conformance.commitments import (
    COMMITMENTS,
    Commitment,
    Evidence,
    EvidenceKind,
    Status,
)
from daale.conformance.lock import (
    CommitmentResult,
    ConformanceReport,
    EvidenceIndex,
    Outcome,
    build_evidence_index,
    evaluate,
    lock,
)
from daale.conformance.report import as_dict, as_json, render

__all__ = [
    "CATEGORY_MEANINGS",
    "CLASSIFICATIONS",
    "COMMITMENTS",
    "Category",
    "Classification",
    "Commitment",
    "CommitmentResult",
    "ConformanceReport",
    "Evidence",
    "EvidenceIndex",
    "EvidenceKind",
    "Outcome",
    "Status",
    "as_dict",
    "as_json",
    "build_evidence_index",
    "by_category",
    "classification_for",
    "evaluate",
    "lock",
    "render",
]
