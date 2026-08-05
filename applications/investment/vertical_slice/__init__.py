"""First complete vertical slice of the YUKTI reasoning pipeline.

One fixed sample document travels the whole pipeline and every stage output is
written to disk, so each intermediate representation can be inspected on its
own rather than inferred from the final report.

    sample document (JSON)
            |
            v  parse.py            -- deserialise + validate. No reasoning.
    InvestmentPacket
            |
            v  investment.translate -- the existing domain translator
    ChoirIR
            |
            v  core.pipeline.execute -- the existing kernels and synthesizer
    Artifacts + Synthesis + Trace  (the canonical record)
            |
            v  core.report.render   -- the existing projection
    Execution report

Only the first arrow is new. Everything from ``InvestmentPacket`` onward is
``choir_prototype`` called as a library, unmodified: the package is frozen and
hash-pinned, and this slice does not touch it.

The one architectural choice the slice makes -- that a "document" for v0.1 is
the deal packet serialised, not free text requiring extraction -- is recorded in
``docs/architecture/DECISION-002_document_intake_for_the_vertical_slice.md``.

Scope is deliberately one path. There is no document-type dispatch, no format
detection, no configuration, and no second sample.
"""
