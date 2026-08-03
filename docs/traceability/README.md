# Traceability

This directory defines how DAALE will track the path from research and
specification artifacts to implementation artifacts.

Traceability must not invent missing links. A link should appear only when the
source artifact exists and the target artifact has a documented relationship to
it.

## Canonical Chain

Use this chain when recording component lineage:

```text
SPEC
-> Concept
-> Architectural Component
-> Implementation File
-> Unit Tests
-> Benchmark
-> Documentation
```

## Rules

- Use exact file paths for implementation, test, benchmark, and documentation
  artifacts.
- Use `Pending` when an artifact category is expected but not yet created.
- Use `Blocked` when an architectural decision is required.
- Do not treat filename similarity as proof of traceability.
- Update traceability rows when files are renamed, deleted, or superseded.
