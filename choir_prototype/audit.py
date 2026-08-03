"""The domain-independence audit.

``choir/research/phase-5-generalization/domain_independence.md`` §6 defines a
falsifiable claim and a way to measure it:

    Onboarding a new domain must require zero changes to the core.
    portability = 1 - (core_changes / total_changes)

That document recorded the metric as **unmeasured**. This module runs it.

The audit is deliberately mechanical. Every check below is a computation over
the source tree or over live pipeline runs -- not an assertion in a docstring.
A layering rule nobody verifies is a layering rule that has already been broken.

    A1  import direction      no core module imports a domain module
    A2  vocabulary isolation  no core module contains domain vocabulary
    A3  execution             every domain runs end to end on shared code
    A4  shared machinery      every domain uses the same runtime/synthesizer
    A5  core stability        core hashes match the pinned manifest
    A6  rule identity         the same decision rules fire across all domains
    A7  hold-out              the control domain needed no core change

A5 and A7 are the load-bearing ones. A7 is the actual experiment: engineering
was written after the manifest in A5 was pinned.
"""

from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass
from pathlib import Path

from choir_prototype.core.pipeline import execute
from choir_prototype.domains import DEVELOPMENT_SET, HOLD_OUT, REGISTRY

CORE_DIR = Path(__file__).resolve().parent / "core"
DOMAIN_DIR = Path(__file__).resolve().parent / "domains"

# Core module hashes, taken over the *normalised syntax tree* rather than raw
# bytes. The claim being measured is "adding a domain required no change to core
# code", and raw-byte hashing cannot distinguish a code change from a formatter
# reflowing a long line -- which is exactly what happened once during this
# experiment and produced a false alarm on core/inspection.py.
#
# AST hashing has the right granularity: it is blind to whitespace, line breaks
# and comments, and sensitive to every identifier, literal, docstring and
# statement. A domain leak cannot hide from it.
#
# PROVENANCE. These were pinned before the hold-out domain (engineering) was
# written. A raw-byte manifest taken at the same moment was verified against the
# tree immediately after engineering was added: all ten core files matched
# byte-for-byte. The manifest was then re-pinned in AST form after a formatter
# pass reflowed one file. See render_audit() for how this is reported.
CORE_MANIFEST = {
    "__init__.py": "3b4f11a8f37d72daab52e60506e8fe6b640acabfb7b6d96c6fd05575dbc53711",
    "contracts.py": "b28f5ff2b2f9c819870dbca6d65c80404b98c0876dcd7ff04ab49c9836fbe043",
    "domain.py": "960440538bab06fd9983b07d1979111370a1c72057a2c2867493aa0fee4dc864",
    "inspection.py": "af92ac656bb7ea21a841b81f616462f9c9be796d3b443f839956c096baa79466",
    "ir.py": "a6fcdda9276ee322c40f56a69977cb183c8cd4186530aaf47aed17a24833162e",
    "pipeline.py": "d155db963a2c160f32795635edb52ac69cf6ad949f348b5f53aca65aa2cc6a42",
    "replay.py": "902003ce6dbc0f8d11c6ce20e48d5e7180c18fb0f3ef6565bfb2780aa36cc87a",
    "report.py": "2641e10a49b3f55b053a027604f9f40cd1dd7252b59c1925ef7914d3aa5f1144",
    "runtime.py": "6e4f3398af63e46009b4337985b93ece5afaa57bb5971c99249e7b8dcb9b13b1",
    "synthesizer.py": "206799e84a42896ebc4b9671e62dbc19fb297ea71f1d18002b10998a3e70a21e",
}

# Words that would betray a domain leak into the core. Drawn from all four
# domains' subject matter -- none of these should appear in core/ source.
DOMAIN_VOCABULARY = (
    "investment",
    "arr_usd",
    "gross_margin",
    "runway",
    "yoga",
    "limitation",
    "claimant",
    "egfr",
    "dialysis",
    "guideline",
    "fatigue",
    "weld",
    "corrosion",
)


@dataclass(frozen=True)
class Check:
    """One audit check and its result."""

    id: str
    name: str
    passed: bool
    detail: str
    rows: tuple[str, ...] = ()


def core_digest(path: Path) -> str:
    """Hash a module's normalised syntax tree.

    Blind to whitespace, line breaks and comments; sensitive to every
    identifier, literal, docstring and statement.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return hashlib.sha256(ast.dump(tree).encode("utf-8")).hexdigest()


def _core_files() -> list[Path]:
    return sorted(CORE_DIR.glob("*.py"))


def _domain_modules() -> list[Path]:
    return sorted(
        path
        for path in DOMAIN_DIR.rglob("*.py")
        if path.name != "__init__.py" or path.parent != DOMAIN_DIR
    )


def _imports(path: Path) -> set[str]:
    """Return every module imported by a source file."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def check_import_direction() -> Check:
    """A1: no core module may import anything from the domain layer."""
    violations: list[str] = []
    for path in _core_files():
        for module in sorted(_imports(path)):
            if "choir_prototype.domains" in module:
                violations.append(f"core/{path.name} imports {module}")
    return Check(
        id="A1",
        name="import direction",
        passed=not violations,
        detail=(
            f"{len(_core_files())} core modules scanned; "
            f"{len(violations)} upward import(s) into domains"
        ),
        rows=tuple(violations),
    )


def _docstring_nodes(tree: ast.Module) -> set[int]:
    """Return the ids of Constant nodes that are docstrings."""
    found: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            body = getattr(node, "body", [])
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                found.add(id(body[0].value))
    return found


def _executable_text(path: Path) -> str:
    """Return a module's identifiers and runtime strings, excluding prose.

    Comments never reach the AST, and docstrings are filtered out explicitly.
    That distinction matters: a docstring naming a domain as an illustration
    creates no dependency, whereas a domain term in an identifier or a runtime
    string literal is real coupling. The first version of this check compared
    raw source text and could not tell the two apart -- it flagged the ordinary
    English word "limitation" in a comment about threading.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docstrings = _docstring_nodes(tree)
    parts: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            parts.append(node.id)
        elif isinstance(node, ast.Attribute):
            parts.append(node.attr)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            parts.append(node.name)
        elif isinstance(node, ast.arg):
            parts.append(node.arg)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) not in docstrings:
                parts.append(node.value)
    return " ".join(parts).lower()


def check_vocabulary_isolation() -> Check:
    """A2: no core module may mention domain subject matter in executable code."""
    violations: list[str] = []
    for path in _core_files():
        text = _executable_text(path)
        for word in DOMAIN_VOCABULARY:
            if word in text:
                violations.append(f"core/{path.name} uses '{word}' in code")
    return Check(
        id="A2",
        name="vocabulary isolation",
        passed=not violations,
        detail=(
            f"{len(DOMAIN_VOCABULARY)} domain terms searched across "
            f"{len(_core_files())} core modules (identifiers and runtime "
            "strings; docstrings and comments excluded)"
        ),
        rows=tuple(violations),
    )


def prose_advisory() -> tuple[str, ...]:
    """Non-blocking: core prose that still names a specific domain.

    Not a failure -- documentation is not coupling -- but worth surfacing so it
    stays visible rather than quietly accumulating. Reported separately from the
    pass/fail checks so it cannot be mistaken for either.
    """
    notes: list[str] = []
    for path in _core_files():
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            lowered = line.lower()
            stripped = lowered.strip()
            if (
                not (
                    stripped.startswith("#")
                    or '"""' in lowered
                    or stripped.startswith(("'", '"'))
                )
                and "investment" not in lowered
            ):
                continue
            for word in ("investment", "jyotish", "clinical packet"):
                if word in lowered:
                    notes.append(f"core/{path.name}:{number} prose mentions '{word}'")
                    break
    return tuple(notes)


def check_execution() -> Check:
    """A3: every registered domain runs end to end on the shared pipeline."""
    rows: list[str] = []
    failures = 0
    for name, domain in REGISTRY.items():
        for packet_id, packet in domain.packets.items():
            try:
                result, synthesis = execute(packet, domain)
                fired = next(
                    (r.name for r in synthesis.rules_evaluated if r.fired), "(none)"
                )
                rows.append(
                    f"{name:<12} {packet_id:<28} "
                    f"{synthesis.recommendation.value:<24} "
                    f"{synthesis.confidence.value:<13} {fired}"
                )
                if not result.artifacts:
                    failures += 1
            except Exception as error:  # noqa: BLE001 - the audit reports, not raises
                failures += 1
                rows.append(f"{name:<12} {packet_id:<28} FAILED: {error}")
    return Check(
        id="A3",
        name="execution",
        passed=failures == 0,
        detail=f"{len(rows)} packet(s) across {len(REGISTRY)} domains executed",
        rows=tuple(rows),
    )


def check_shared_machinery() -> Check:
    """A4: no domain supplies its own runtime, synthesizer or confidence rule."""
    forbidden = ("def synthesize", "def run_kernels", "def derive_confidence")
    violations: list[str] = []
    for path in _domain_modules():
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            if marker in text:
                violations.append(f"{path.name} defines its own {marker.split()[1]}")
    return Check(
        id="A4",
        name="shared machinery",
        passed=not violations,
        detail=(
            f"{len(_domain_modules())} domain modules scanned for private "
            "reasoning machinery"
        ),
        rows=tuple(violations),
    )


def check_core_stability() -> Check:
    """A5: core file hashes match the manifest pinned before the hold-out."""
    rows: list[str] = []
    drift = 0
    for path in _core_files():
        digest = core_digest(path)
        expected = CORE_MANIFEST.get(path.name)
        if expected is None:
            rows.append(f"{path.name:<18} NEW FILE (not in manifest)")
            drift += 1
        elif expected != digest:
            rows.append(f"{path.name:<18} CHANGED since manifest")
            drift += 1
        else:
            rows.append(f"{path.name:<18} unchanged  {digest[:16]}")
    missing = set(CORE_MANIFEST) - {p.name for p in _core_files()}
    for name in sorted(missing):
        rows.append(f"{name:<18} REMOVED since manifest")
        drift += 1
    rows.append("")
    rows.append("hashes are over the normalised syntax tree, not raw bytes: blind to")
    rows.append("formatting, sensitive to every identifier, literal and statement.")
    rows.append("manifest pinned before the hold-out domain was written; re-pinned in")
    rows.append(
        "AST form after a formatter reflowed one file (see CORE_MANIFEST note)."
    )
    return Check(
        id="A5",
        name="core stability",
        passed=drift == 0,
        detail=f"{len(CORE_MANIFEST)} pinned core files; {drift} changed",
        rows=tuple(rows),
    )


def check_rule_identity() -> Check:
    """A6: the same decision rules serve every domain.

    Every run, in every domain, is adjudicated by one rule from the same fixed
    ordered set. If a domain needed its own rules, this would show it.
    """
    rule_names: set[tuple[str, ...]] = set()
    fired_by_domain: dict[str, list[str]] = {}
    for name, domain in REGISTRY.items():
        for packet_id, packet in domain.packets.items():
            _, synthesis = execute(packet, domain)
            rule_names.add(tuple(r.name for r in synthesis.rules_evaluated))
            fired = next(
                (r.name for r in synthesis.rules_evaluated if r.fired), "(none)"
            )
            fired_by_domain.setdefault(name, []).append(f"{packet_id} -> {fired}")

    # Every evaluated sequence must be a prefix of the same rule ordering.
    longest = max(rule_names, key=len) if rule_names else ()
    consistent = all(longest[: len(seq)] == seq for seq in rule_names)

    fired_set = {
        row.split("-> ")[1] for rows in fired_by_domain.values() for row in rows
    }
    rows = [f"rule order: {' -> '.join(longest)}", f"rules exercised: {len(fired_set)}"]
    for name, entries in fired_by_domain.items():
        for entry in entries:
            rows.append(f"  {name:<12} {entry}")

    return Check(
        id="A6",
        name="rule identity",
        passed=consistent,
        detail=(
            f"{len(rule_names)} distinct evaluation prefix(es), all from one "
            f"ordering; {len(fired_set)} of {len(longest)} rules exercised"
        ),
        rows=tuple(rows),
    )


def check_hold_out() -> Check:
    """A7: the hold-out domain required no core change.

    Law and medicine were the development set -- the core was being decoupled
    while they were written, so a fix could have been tuned to them. Engineering
    was written afterwards, against a core already pinned by A5's manifest.
    """
    rows: list[str] = []
    for name in DEVELOPMENT_SET:
        rows.append(f"development set : {name}")
    for name in HOLD_OUT:
        domain = REGISTRY.get(name)
        rows.append(
            f"HOLD-OUT        : {name} "
            f"({len(domain.kernels) if domain else 0} kernels, "
            f"{len(domain.packets) if domain else 0} packet(s))"
        )
    core_ok = check_core_stability().passed
    rows.append(
        "core hashes after adding the hold-out: "
        + ("unchanged" if core_ok else "CHANGED")
    )
    return Check(
        id="A7",
        name="hold-out",
        passed=core_ok and bool(HOLD_OUT),
        detail=(
            f"{len(DEVELOPMENT_SET)} development domains, "
            f"{len(HOLD_OUT)} held out as a control"
        ),
        rows=tuple(rows),
    )


def run_audit() -> tuple[Check, ...]:
    """Run every check, in order."""
    return (
        check_import_direction(),
        check_vocabulary_isolation(),
        check_execution(),
        check_shared_machinery(),
        check_core_stability(),
        check_rule_identity(),
        check_hold_out(),
    )


def portability_score() -> tuple[int, int, float]:
    """Return (core_changes, domain_additions, portability).

    Per domain_independence.md §6:  portability = 1 - core_changes / total.
    """
    core_changes = sum(
        1 for path in _core_files() if CORE_MANIFEST.get(path.name) != core_digest(path)
    )
    domain_additions = len(_domain_modules())
    total = core_changes + domain_additions
    portability = 1.0 - (core_changes / total) if total else 0.0
    return core_changes, domain_additions, portability


def render_audit() -> str:
    """Format the audit for the terminal."""
    width = 78
    checks = run_audit()
    core_changes, domain_additions, portability = portability_score()

    lines = [
        "=" * width,
        "CHOIR DOMAIN-INDEPENDENCE AUDIT",
        "=" * width,
        "Measures the claim defined in domain_independence.md section 6:",
        "  onboarding a new domain must require zero changes to the core.",
        "",
        f"Domains registered : {', '.join(REGISTRY)}",
        f"Core modules       : {len(_core_files())}",
        f"Domain modules     : {len(_domain_modules())}",
        "",
    ]

    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        lines.append("-" * width)
        lines.append(f"[{status}] {check.id}  {check.name}")
        lines.append(f"       {check.detail}")
        for row in check.rows:
            lines.append(f"       {row}")

    advisory = prose_advisory()
    lines.append("-" * width)
    lines.append("[note] advisory  core prose naming a specific domain")
    lines.append(
        f"       {len(advisory)} mention(s). Documentation, not coupling -- "
        "reported so it stays visible."
    )
    for row in advisory:
        lines.append(f"       {row}")

    lines.append("=" * width)
    lines.append("PORTABILITY SCORE")
    lines.append("=" * width)
    lines.append(f"  core changes required to add domains : {core_changes}")
    lines.append(f"  domain modules added                 : {domain_additions}")
    lines.append(
        f"  portability = 1 - {core_changes}/{core_changes + domain_additions}"
        f" = {portability:.2f}"
    )
    lines.append("")

    if all(check.passed for check in checks):
        lines.append("RESULT: domain independence HOLDS for the four domains tested.")
        lines.append("")
        lines.append("What this does and does not establish:")
        lines.append("  DOES: four domains with different packet shapes, vocabularies")
        lines.append("        and subject matter share one IR, one runtime, one")
        lines.append("        confidence model, one conflict model and one decision")
        lines.append("        procedure, with the core provably untouched.")
        lines.append("  DOES NOT: prove independence for domains unlike these four.")
        lines.append("        Deontic depth and graded defeat remain untested; see")
        lines.append("        domain_independence.md section 7, falsifiers F3 and F7.")
    else:
        lines.append("RESULT: domain independence DOES NOT HOLD. See failures above.")

    return "\n".join(lines)
