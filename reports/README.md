# Reports

This directory is reserved for Prototype-001 report output.

Two other producers now write here. Both are generated output that is not
committed, which is why they share this tree rather than claiming their own:

- `reports/vertical-slice/<packet-id>/` — stage artifacts from
  `applications/investment/vertical_slice`.
- `reports/workspace/<case-id>/` — the investment workspace's case files and the
  reasoning record behind each judgment.

The workspace stores institutional state here, not report output. That stretches
this directory's stated purpose; the reasoning is recorded in
`docs/architecture/DECISION-003_product_application_architecture.md` and in
`docs/development/IMPLEMENTATION_LOG.md` (assumption B6). A fourth producer
should prompt a convention rather than a third stretch.

The infrastructure utilities may create dated report directories in this form:

```text
reports/
    YYYY-MM-DD/
        report.md
        metadata.json
```

Do not commit generated report files unless a future specification explicitly
requires that behavior.
