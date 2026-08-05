"""The YUKTI investment case workspace.

Version 1 of the institutional product. A committee opens a case, assembles the
diligence material against a standard schedule, requests an institutional
judgment, reads what the review areas concluded and where they disagreed, and
records its decision.

The reasoning engine is infrastructure here. The workspace calls
``applications.investment.vertical_slice`` and reads back the record it wrote;
it does not import CHOIR internals, and a user never sees a kernel, a
translator, an intermediate representation or a runtime artifact. The one place
those surface is the audit view, which exists precisely so a decision can be
defended.

    cases.py       the institution's unit of work, and where it is kept
    diligence.py   the standard diligence schedule and intake vocabulary
    analysis.py    the only door to the engine; projects the record for reading
    server.py      the application server
    ui/            the workspace itself
"""
