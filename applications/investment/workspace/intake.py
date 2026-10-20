"""Reading messy prose into *proposed* figures. Nothing here becomes material.

The workspace's intake screens assume the diligence pack is already structured.
Real material is not: it arrives as a memo, a deck summary, a paragraph in an
email. This module reads that prose and proposes what it thinks the material
says, so a person can confirm it instead of retyping it.

The boundary, and why it is exactly here
----------------------------------------

``DECISION-002`` approved *"documents may represent packets; they may not
interpret them"* and explicitly declined prose-plus-extraction, on the grounds
that deciding a sentence asserts ``net_revenue_retention_pct = 104`` is
interpretation — "an unaudited reasoning step in front of the audited ones".

That objection is about what reaches the **engine**, and it stands. Nothing in
this module reaches the engine, or the case store, or a material digest. It
returns *proposals*: read-only suggestions, each carrying the span of prose it
came from, that a person must accept, edit or reject. The figure that eventually
enters material is authored by that person, exactly as it is today when they
type it into the diligence schedule — the only difference is that this one
arrives with the sentence it came from attached.

That difference is the point. ``CHOIR_v0.1_RESEARCH_FREEZE.md`` §4.3 records the
gap as *"evidence cites a source label, not a locus in an edition"*, and the
implementation log records that "evidence formation is still unrecorded… material
identity now records *that* they did it and when, but not *why* or *from what*".
A confirmed proposal records the *from what*. See ``DECISION-008``.

What this is, mechanically
--------------------------

A deterministic reader over the fifteen metrics the diligence schedule already
names. No model, no network, no learning. Same prose in, same proposals out —
which is what makes it testable, and what makes the confirmation step a real
check rather than a rubber stamp on something nobody can reproduce.

``propose_from_assistant`` is the seam a language model would occupy. It is
declared and unimplemented on purpose: wiring one is a decision about authority,
not a refactor, and it must produce the same ``Proposal`` shape — span included,
confirmation still required — or it is not the same architecture.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from applications.investment.workspace.cases import Source
from applications.investment.workspace.diligence import SCHEDULE

# How a source's standing suggests a figure's standing. A mapping offered as a
# starting point for the reader, never a conclusion: the confirm step shows this
# field and the reader changes it if the prose says otherwise.
_KIND_TO_STATUS = {
    "audit": "confirmed",
    "management": "reported",
    "interview": "reported",
    "third_party": "estimated",
    "assertion": "unknown",
}

# Trigger phrases per metric, longest first so the most specific wins: a
# sentence about "market growth" must not be read as "growth".
_TRIGGERS: dict[str, tuple[str, ...]] = {
    "net_revenue_retention_pct": (
        "net revenue retention",
        "net dollar retention",
        "nrr",
    ),
    "top_customer_revenue_pct": (
        "largest customer",
        "top customer",
        "biggest customer",
        "customer concentration",
    ),
    "market_growth_pct": ("market growth", "market is growing", "segment growth"),
    "gross_margin_pct": ("gross margin",),
    "net_burn_monthly_usd": ("net burn", "monthly burn", "burn rate", "burning"),
    "founder_voting_control_pct": (
        "voting control",
        "founder control",
        "voting rights",
    ),
    "independent_board_seats": (
        "independent board",
        "independent director",
        "board seat",
    ),
    "competitor_count": ("competitor", "competing vendor", "direct rival"),
    "logo_churn_pct": ("logo churn", "customer churn", "churn"),
    "yoy_growth_pct": (
        "year-over-year",
        "year over year",
        "yoy",
        "annual growth",
        "grew",
        "growth",
    ),
    "tam_usd": ("addressable market", "tam", "market size", "market sizing"),
    "cash_usd": ("cash on hand", "cash balance", "cash at bank", "cash"),
    "arr_usd": ("annual recurring revenue", "arr", "recurring revenue", "revenue"),
    "audit_status": ("audited", "unaudited", "audit status"),
    "reporting_cadence": ("reporting cadence", "reports monthly", "reporting"),
}

_UNIT_BY_METRIC = {item.metric: item.unit for item in SCHEDULE}
_LABEL_BY_METRIC = {item.metric: item.label for item in SCHEDULE}

# Scale suffixes on a money figure. "bn" before "b" so the longer one wins.
_SCALES: tuple[tuple[str, float], ...] = (
    ("trillion", 1e12),
    ("billion", 1e9),
    ("million", 1e6),
    ("thousand", 1e3),
    ("bn", 1e9),
    ("tn", 1e12),
    ("k", 1e3),
    ("m", 1e6),
    ("b", 1e9),
)

# One pattern for every number, classified afterwards. Reading them all in one
# pass is what lets a sentence naming three metrics give each its own figure.
_NUMBER = re.compile(
    r"(?P<symbol>[$£€]\s?)?"
    r"(?P<number>\d[\d,]*(?:\.\d+)?)"
    r"\s*(?P<scale>trillion|billion|million|thousand|bn|tn|[kmb])?"
    r"\s*(?P<percent>%|per ?cent|percent)?",
    re.IGNORECASE,
)

# A bare four-digit number in this range is a year far more often than it is a
# figure. "FY2024" was being read as annual recurring revenue before this.
_YEAR = re.compile(r"^(19|20)\d{2}$")

# Documents a memo names, and what the register would call them. A memo that
# says "per the independent audit" has named its own source; a reader should be
# able to confirm that rather than retype it before any figure can cite it.
_SOURCE_PATTERNS: tuple[tuple[str, str, str, str], ...] = (
    ("independent audit", "SRC-AUDIT", "Independent audit of the statements", "audit"),
    ("audited statements", "SRC-AUDIT", "Independent audit of the statements", "audit"),
    ("audited financial", "SRC-AUDIT", "Independent audit of the statements", "audit"),
    ("the audit", "SRC-AUDIT", "Independent audit of the statements", "audit"),
    ("auditor", "SRC-AUDIT", "Independent audit of the statements", "audit"),
    ("capitalisation table", "SRC-CAPTABLE", "Certified capitalisation table", "audit"),
    ("capitalization table", "SRC-CAPTABLE", "Certified capitalisation table", "audit"),
    ("cap table", "SRC-CAPTABLE", "Certified capitalisation table", "audit"),
    ("management deck", "SRC-DECK", "Management investor deck", "management"),
    ("investor deck", "SRC-DECK", "Management investor deck", "management"),
    ("the deck", "SRC-DECK", "Management investor deck", "management"),
    ("management accounts", "SRC-DECK", "Management accounts", "management"),
    ("market sizing", "SRC-MARKET", "Third-party market sizing report", "third_party"),
    ("sector note", "SRC-MARKET", "Third-party sector research", "third_party"),
    ("trade association", "SRC-MARKET", "Trade association research", "third_party"),
    ("third-party", "SRC-MARKET", "Third-party research", "third_party"),
    ("third party", "SRC-MARKET", "Third-party research", "third_party"),
    ("analyst report", "SRC-MARKET", "Third-party research", "third_party"),
    ("reference call", "SRC-CUSTOMER", "Reference calls with customers", "interview"),
    ("customer call", "SRC-CUSTOMER", "Reference calls with customers", "interview"),
    (
        "customer interview",
        "SRC-CUSTOMER",
        "Reference calls with customers",
        "interview",
    ),
    ("founder email", "SRC-FOUNDER", "Founder email summary", "assertion"),
    ("founder summary", "SRC-FOUNDER", "Founder email summary", "assertion"),
    ("email summary", "SRC-FOUNDER", "Founder email summary", "assertion"),
    (
        "management told us",
        "SRC-FOUNDER",
        "Unsupported management assertion",
        "assertion",
    ),
)

# A source mention is only worth registering if the prose asserts the document
# *exists and is held*. The same phrase can carry the opposite claim -- "we
# don't have a cap table", "the cap table wasn't provided", "the cap table is
# still outstanding" -- and an assertion of absence is not a weak assertion of
# presence. Three standings, and only the first instantiates a source:
_MENTION_PRESENT = "present"  # asserted to exist and be in hand
_MENTION_ABSENT = "absent"  # asserted not to exist or not to have been provided
_MENTION_UNKNOWN = "unknown"  # named, but existence not asserted either way

# Tokens that close the scope of an earlier negation, so it cannot reach a
# phrase in a later clause. "We doubt the numbers, but the cap table is clean"
# is a present cap table; a colon starts a fresh assertion ("Per the audit:
# revenue is ..."). Commas are deliberately *not* here -- "nothing on X, Y, or
# the cap table" must keep the negation across the list.
_SCOPE_RESET = re.compile(
    r"(?s).*(?:"
    r":|\bbut\b|\bhowever\b|\bthough\b|\balthough\b|\bwhereas\b|"
    r"\baside from\b|\bother than\b|\bexcept\b"
    r")"
)

# Negation in the run-up to the phrase. Whole words plus the -n't contraction,
# so "Now" and "annotation" do not trip it.
_ABSENCE_BEFORE = re.compile(
    r"\b(?:no|not|none|nothing|neither|nor|without|lack|lacks|lacking|"
    r"missing|absent|never|zero)\b|n['’]t\b"
)

# Negation attached to a delivery verb just after the phrase, within its own
# clause: "cap table wasn't provided", "... is not available", "... never
# shared", "... n/a".
_ABSENCE_AFTER = re.compile(
    r"(?:\bnot\b|\bnever\b|n['’]t)\b[\w\s]{0,20}?\b(?:provided|shared|"
    r"supplied|available|attached|included|disclosed|furnished|received|sent|"
    r"on file)\b"
    r"|\bunavailable\b|\bnot available\b|\bn/?a\b"
)

# Named, but its existence is not asserted -- it was asked for, is awaited, or
# was merely referred to in passing.
_MENTION_ONLY = re.compile(
    r"\b(?:discussed|mentioned|referenced|asked for|requested|to be provided|"
    r"to follow|to come|chase|chasing|awaited|awaiting|outstanding|pending|"
    r"expected|promised|yet to|still to|still with the company|"
    r"will (?:provide|send|share|follow)|"
    r"(?:have|haven['’]t|has not|not) (?:yet )?(?:seen|been provided))\b"
)

# A clause ends at any of these. Used to bound the window after the phrase so a
# negation two clauses on cannot reach back to it.
_CLAUSE_AFTER = re.compile(r"[,;:.—]|\s-\s")

_AUDIT_WORDS = (
    ("unaudited", "unaudited"),
    ("not been audited", "unaudited"),
    ("audited", "audited"),
    ("reviewed", "reviewed"),
)
_CADENCE_WORDS = ("monthly", "quarterly", "annually", "annual", "weekly", "ad hoc")


@dataclass(frozen=True)
class ProposedSource:
    """A document the prose names, offered for the source register.

    Same rule as a figure: proposed, never registered. A reader confirms that
    "per the independent audit" means a document they actually hold before any
    figure is allowed to cite it.
    """

    label: str
    origin: str
    kind: str
    quote: str


@dataclass(frozen=True)
class Span:
    """Where in the supplied text a proposal came from.

    Offsets are into the text exactly as pasted, so the surface can highlight
    the passage rather than quote it out of context.
    """

    start: int
    end: int
    quote: str


@dataclass(frozen=True)
class Proposal:
    """One suggested figure. Not material until a person accepts it.

    ``basis`` says *why* this was proposed — the phrase that triggered it and
    how the number was read. It exists so the confirm step is a judgement about
    a stated reading, rather than a guess about an opaque one.
    """

    metric: str
    label: str
    unit: str
    value: str
    status: str
    source_label: str
    span: Span
    basis: str

    @property
    def needs_attention(self) -> bool:
        """True when the reader must supply something the prose did not."""
        return not self.source_label


# A sentence ends at a full stop followed by space or end of line, at a
# semicolon, or at a line break. Not at any full stop: `$1.4M` and `FY2024` are
# one token each, and splitting them was reading burn as "$1".
_SENTENCE_END = re.compile(r"(?<=[.;])\s+|\r?\n+")


def _sentences(text: str) -> list[tuple[int, str]]:
    """Split into sentence-ish spans, keeping each one's offset into the text.

    Bounded deliberately: a number in one sentence must not be attached to a
    metric named in another. Newlines end a span too, because pasted material is
    usually bullets rather than prose.
    """
    spans: list[tuple[int, str]] = []
    cursor = 0
    for match in _SENTENCE_END.finditer(text):
        chunk = text[cursor : match.start()]
        if chunk.strip():
            spans.append((cursor, chunk))
        cursor = match.end()
    tail = text[cursor:]
    if tail.strip():
        spans.append((cursor, tail))
    return spans


def _enclosing_sentence(text: str, index: int) -> tuple[int, int]:
    """The bounds of the sentence containing ``index``, per ``_SENTENCE_END``.

    Negation is read within one sentence and no further: a full stop or a line
    break between two clauses means the second does not inherit the first's
    "no".
    """
    start = 0
    for match in _SENTENCE_END.finditer(text):
        if match.start() > index:
            return start, match.start()
        start = match.end()
    return start, len(text)


def _mention_standing(text: str, start: int, end: int) -> str:
    """Classify one source mention: present, absent, or merely named.

    Looks at the run-up to the phrase (back to the last scope-resetting token)
    and at the phrase's own clause. A negator in front ("no cap table",
    "nothing on ... the cap table"), or a negated delivery verb behind it ("cap
    table wasn't provided"), reads as absent. Language that only refers to the
    document ("the cap table was discussed", "still outstanding") reads as
    unknown. Anything else is a present, held document.
    """
    sentence_start, sentence_end = _enclosing_sentence(text, start)
    before = text[sentence_start:start].lower()
    after = text[end:sentence_end].lower()

    reset = _SCOPE_RESET.match(before)
    if reset:
        before = before[reset.end() :]

    after_clause = _CLAUSE_AFTER.split(after, 1)[0]

    if _ABSENCE_BEFORE.search(before) or _ABSENCE_AFTER.search(after_clause):
        return _MENTION_ABSENT
    if _MENTION_ONLY.search(before) or _MENTION_ONLY.search(after_clause):
        return _MENTION_UNKNOWN
    return _MENTION_PRESENT


def _clean_number(raw: str) -> float | None:
    try:
        return float(raw.replace(",", ""))
    except ValueError:
        return None


def _scale_for(suffix: str | None) -> float:
    if not suffix:
        return 1.0
    lowered = suffix.lower()
    for token, factor in _SCALES:
        if lowered == token:
            return factor
    return 1.0


def _format_number(value: float) -> str:
    """Render a parsed number the way the diligence schedule stores figures."""
    if value == int(value):
        return str(int(value))
    return f"{value:g}"


@dataclass(frozen=True)
class _Number:
    """One number found in a sentence, with where it sat and how it read."""

    position: int
    text: str
    value: float
    is_money: bool
    is_percent: bool
    is_year: bool


def _numbers_in(sentence: str) -> list[_Number]:
    """Every number in a sentence, classified by how it was written."""
    found: list[_Number] = []
    for match in _NUMBER.finditer(sentence):
        raw = _clean_number(match.group("number"))
        if raw is None:
            continue
        scale = match.group("scale")
        symbol = match.group("symbol")
        percent = match.group("percent")
        found.append(
            _Number(
                position=match.start(),
                text=match.group(0).strip(),
                value=raw * _scale_for(scale),
                is_money=bool(symbol) or bool(scale),
                is_percent=bool(percent),
                is_year=bool(_YEAR.match(match.group("number"))),
            )
        )
    return found


def _compatible(metric: str, number: _Number) -> bool:
    """Whether a number could plausibly be this metric's value.

    Unit-led, and deliberately strict about the two ways this misreads prose:
    a year is not a money figure, and a bare integer is not a percentage.
    """
    unit = _UNIT_BY_METRIC.get(metric, "")
    if unit == "USD":
        return (number.is_money or number.value >= 10_000) and not number.is_year
    if unit == "%":
        return number.is_percent
    if unit == "count":
        return not number.is_money and not number.is_percent and not number.is_year
    return False


def _read_text(metric: str, sentence: str) -> tuple[str, str] | None:
    lowered = sentence.lower()
    if metric == "audit_status":
        for phrase, value in _AUDIT_WORDS:
            if phrase in lowered:
                return value, phrase
        return None
    for word in _CADENCE_WORDS:
        if word in lowered:
            return word, word
    return None


def _source_keywords(source: Source) -> tuple[str, ...]:
    """Distinctive words from a source's own description, for attribution."""
    words = re.findall(r"[a-z0-9]{4,}", source.origin.lower())
    skip = {"from", "with", "this", "that", "their", "than", "report", "statements"}
    return tuple(word for word in words if word not in skip)


def _attribute(sentence: str, sources: tuple[Source, ...]) -> tuple[str, str]:
    """Find which registered source a sentence points at. ('' , '') if none.

    Label first, because a memo that names ``SRC-DECK`` has said so outright.
    Then distinctive words from the source's own description, which is how a
    person reads "per the FY2024 audit" as the audit in the register.
    """
    lowered = sentence.lower()
    for source in sources:
        if source.label.lower() in lowered:
            return source.label, f"names {source.label}"

    # Longest matching keyword wins, not the first source in the register.
    # "certified capitalisation table" must beat the "independent" in
    # "independent board seat", which otherwise pulled the audit source in.
    best: tuple[int, str, str] | None = None
    for source in sources:
        for keyword in _source_keywords(source):
            if keyword in lowered and (best is None or len(keyword) > best[0]):
                best = (len(keyword), source.label, keyword)
    if best is None:
        return "", ""
    return best[1], f"'{best[2]}' matches {best[1]}"


def _triggers_in(sentence: str) -> list[tuple[int, int, str, str]]:
    """Every metric this sentence names: (specificity, position, metric, phrase).

    Sorted most-specific first. Specificity is the trigger's length, which is
    what keeps "market growth" from being read as "growth" and "net revenue
    retention" from being read as "revenue" — the longer phrase claims the
    sentence, and its number, before the shorter one gets a turn.
    """
    lowered = sentence.lower()
    hits: dict[str, tuple[int, int, str, str]] = {}
    for metric, triggers in _TRIGGERS.items():
        for trigger in triggers:
            at = lowered.find(trigger)
            if at == -1:
                continue
            candidate = (len(trigger), at, metric, trigger)
            if metric not in hits or candidate[0] > hits[metric][0]:
                hits[metric] = candidate
    return sorted(hits.values(), key=lambda item: (-item[0], item[1]))


@dataclass(frozen=True)
class Reading:
    """Everything one block of prose proposed: its sources and its figures."""

    sources: tuple[ProposedSource, ...]
    figures: tuple[Proposal, ...]


def propose_sources(
    text: str, registered: tuple[Source, ...] = ()
) -> tuple[ProposedSource, ...]:
    """Name the documents this prose refers to, in order of first mention.

    A memo cites its own sources — "per the independent audit", "in the deck".
    Without this the register stays empty, every figure is unattributable, and
    the reader has to leave the conversation to type five source rows before
    anything they pasted can be recorded.

    A mention only counts if the prose asserts the document exists and is held.
    "We don't have a cap table", "the cap table wasn't provided" and "the cap
    table is still outstanding" all name a cap table; none of them registers a
    source, because an assertion of absence is not a weak assertion of presence.
    Every occurrence of every trigger is checked, and a source is proposed at
    the first position where it is asserted present.

    A source already in the register is not proposed again.
    """
    lowered = text.lower()
    have = {source.label for source in registered}
    found: dict[str, ProposedSource] = {}
    position: dict[str, int] = {}
    for phrase, label, origin, kind in _SOURCE_PATTERNS:
        if label in have:
            continue
        at = lowered.find(phrase)
        while at != -1:
            standing = _mention_standing(text, at, at + len(phrase))
            if standing == _MENTION_PRESENT and (
                label not in position or at < position[label]
            ):
                found[label] = ProposedSource(
                    label=label, origin=origin, kind=kind, quote=phrase
                )
                position[label] = at
            at = lowered.find(phrase, at + 1)
    return tuple(sorted(found.values(), key=lambda item: position[item.label]))


def propose(text: str, sources: tuple[Source, ...] = ()) -> tuple[Proposal, ...]:
    """Read prose and propose figures. Returns suggestions, never material.

    One proposal per metric at most, taken from the first sentence that names
    it, so the result is stable and a reader is not asked to arbitrate between
    two readings of the same figure. A metric the prose does not establish
    simply does not appear — this never guesses a value to fill the schedule,
    for the same reason the diligence screen records a blank as a gap.
    """
    proposals: list[Proposal] = []
    claimed: set[str] = set()

    for offset, sentence in _sentences(text):
        numbers = _numbers_in(sentence)
        taken: set[int] = set()
        source_label, attribution = _attribute(sentence, sources)

        # Most specific metric first, each consuming the nearest number it could
        # plausibly own. One sentence can therefore name three figures without
        # any of them stealing another's value.
        for _, position, metric, phrase in _triggers_in(sentence):
            if metric in claimed:
                continue
            if _UNIT_BY_METRIC.get(metric, "") == "text":
                reading = _read_text(metric, sentence)
                if reading is None:
                    continue
                value, read_text = reading
            else:
                usable = [
                    number
                    for index, number in enumerate(numbers)
                    if index not in taken and _compatible(metric, number)
                ]
                if not usable:
                    continue
                nearest = min(usable, key=lambda item: abs(item.position - position))
                taken.add(numbers.index(nearest))
                value = _format_number(nearest.value)
                read_text = nearest.text

            status = _KIND_TO_STATUS.get(
                next(
                    (item.kind for item in sources if item.label == source_label),
                    "",
                ),
                "unknown",
            )
            quote = sentence.strip()
            start = offset + (len(sentence) - len(sentence.lstrip()))
            basis = f"'{phrase}' -> read {read_text}"
            if attribution:
                basis = f"{basis}; {attribution}"
            else:
                basis = f"{basis}; no source named -- pick one before accepting"

            proposals.append(
                Proposal(
                    metric=metric,
                    label=_LABEL_BY_METRIC.get(metric, metric),
                    unit=_UNIT_BY_METRIC.get(metric, ""),
                    value=value,
                    status=status,
                    source_label=source_label,
                    span=Span(start=start, end=start + len(quote), quote=quote),
                    basis=basis,
                )
            )
            claimed.add(metric)

    order = {item.metric: index for index, item in enumerate(SCHEDULE)}
    return tuple(sorted(proposals, key=lambda item: order.get(item.metric, 99)))


def read(text: str, registered: tuple[Source, ...] = ()) -> Reading:
    """Read one block of prose into proposed sources and proposed figures.

    Figures are attributed against the register *plus* whatever sources this
    same text named, so a memo carrying both reads in one pass. Nothing here is
    recorded: the reader confirms the sources and the figures together.
    """
    proposed = propose_sources(text, registered)
    attributable = registered + tuple(
        Source(label=item.label, origin=item.origin, kind=item.kind)
        for item in proposed
    )
    return Reading(sources=proposed, figures=propose(text, attributable))


def propose_from_assistant(
    text: str, sources: tuple[Source, ...] = ()
) -> tuple[Proposal, ...]:
    """The seam a language model would occupy. Deliberately unimplemented.

    A model may read the prose and propose; it may not decide. Whatever fills
    this must return the same ``Proposal`` shape — every suggestion carrying the
    span it came from, and every suggestion still requiring a person to accept
    it — because that shape is what keeps the model a proposer rather than an
    author, per ``DECISION-001`` and ``DECISION-008``.

    Delegates to ``assistant.propose`` when a key is configured, and raises
    ``AssistantUnavailable`` otherwise so the caller falls back to the reader
    above. Imported here rather than at module scope: this module must keep
    working, and keep being importable, with no SDK and no key present.
    """
    from applications.investment.workspace import assistant

    return assistant.propose(text, sources)
