"""The V0.1 freeze.

The prototype is frozen. This module records what "frozen" means precisely
enough to be checked by a machine rather than remembered by a person:

    python -m choir_prototype --frozen

Every file in the package is pinned. Python modules are pinned by *normalised
syntax tree*, so the freeze survives a formatter pass but catches any change to
an identifier, literal, docstring or statement. Everything else is pinned by
content hash.

The individual digests are combined into one **tree digest** -- a single value
that identifies the whole frozen state. Two people can compare that one string
and know they are looking at the same architecture.

WHAT THE FREEZE PROTECTS

Not the code as text. The architecture: the pipeline stages and their order, the
IR shape, the kernel contract, the confidence derivation, the decision rules and
their ordering, the core/domain boundary, and the guarantee that renderers are
pure projections of the record.

V0.2 is expected to change things. The freeze is not a prohibition; it is a
tripwire, so that a change to the architecture is a deliberate act with a version
bump attached rather than something that happens by accident on a Tuesday.
"""

from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass
from pathlib import Path

VERSION = "0.1"
STATUS = "FROZEN"

PACKAGE_DIR = Path(__file__).resolve().parent

# Files excluded from the freeze: caches, and the manifest itself (which cannot
# contain its own hash).
EXCLUDED_NAMES = frozenset({"freeze.py"})
EXCLUDED_PARTS = frozenset({"__pycache__"})


@dataclass(frozen=True)
class FileState:
    """One file's frozen identity."""

    path: str
    digest: str
    kind: str


def _digest(path: Path) -> tuple[str, str]:
    """Return (digest, kind) for one file.

    Python modules hash their syntax tree so the freeze is not tripped by
    reformatting; everything else hashes raw bytes.
    """
    if path.suffix == ".py":
        tree = ast.parse(path.read_text(encoding="utf-8"))
        return hashlib.sha256(ast.dump(tree).encode("utf-8")).hexdigest(), "ast"
    return hashlib.sha256(path.read_bytes()).hexdigest(), "bytes"


def frozen_files() -> list[Path]:
    """Every file covered by the freeze, in a stable order."""
    found = [
        path
        for path in PACKAGE_DIR.rglob("*")
        if path.is_file()
        and path.name not in EXCLUDED_NAMES
        and not EXCLUDED_PARTS & set(path.parts)
    ]
    return sorted(found, key=lambda item: item.relative_to(PACKAGE_DIR).as_posix())


def current_state() -> tuple[FileState, ...]:
    """Compute the current identity of every frozen file."""
    states = []
    for path in frozen_files():
        digest, kind = _digest(path)
        states.append(
            FileState(
                path=path.relative_to(PACKAGE_DIR).as_posix(),
                digest=digest,
                kind=kind,
            )
        )
    return tuple(states)


def tree_digest(states: tuple[FileState, ...] | None = None) -> str:
    """One value identifying the whole frozen state."""
    states = current_state() if states is None else states
    payload = "\n".join(f"{item.path}:{item.kind}:{item.digest}" for item in states)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# The pinned manifest
# ---------------------------------------------------------------------------

FROZEN_TREE_DIGEST = "4771ed0b3591289e75e66214f1fe1f02a63046800aa389d29be2cc66cebb580d"

FROZEN_MANIFEST: dict[str, str] = {
    "FROZEN.md": "964d604635104baf75dcfa86dc491c5feedded84fa1e5e3a042fef778ac5db41",
    "README.md": "c23b99d9d003e67a1d3ac8f181f075da9ffa6d7f39d4086eb258dd67616f0df0",
    "__init__.py": "b8fb696542d55fa813c524776947721f155d99c66e66fba36655069927452de6",
    "__main__.py": "afa1a804e30679ea7afc3008b24a4499cc9266e33462d543fa8ece5b18703508",
    "audit.py": "dba1ad2f3c77423348f574155f2586136fbecfa12764f7ee08de0c928f459da0",
    "core/__init__.py": "3b4f11a8f37d72daab52e60506e8fe6b640acabfb7b6d96c6fd05575dbc53711",
    "core/contracts.py": "b28f5ff2b2f9c819870dbca6d65c80404b98c0876dcd7ff04ab49c9836fbe043",
    "core/domain.py": "960440538bab06fd9983b07d1979111370a1c72057a2c2867493aa0fee4dc864",
    "core/inspection.py": "af92ac656bb7ea21a841b81f616462f9c9be796d3b443f839956c096baa79466",
    "core/ir.py": "a6fcdda9276ee322c40f56a69977cb183c8cd4186530aaf47aed17a24833162e",
    "core/pipeline.py": "d155db963a2c160f32795635edb52ac69cf6ad949f348b5f53aca65aa2cc6a42",
    "core/replay.py": "902003ce6dbc0f8d11c6ce20e48d5e7180c18fb0f3ef6565bfb2780aa36cc87a",
    "core/report.py": "2641e10a49b3f55b053a027604f9f40cd1dd7252b59c1925ef7914d3aa5f1144",
    "core/runtime.py": "6e4f3398af63e46009b4337985b93ece5afaa57bb5971c99249e7b8dcb9b13b1",
    "core/synthesizer.py": "206799e84a42896ebc4b9671e62dbc19fb297ea71f1d18002b10998a3e70a21e",
    "domains/__init__.py": "5d8cac0d1d599d21452ea9606438515971efe13ff58c46568544b4944bcca42b",
    "domains/engineering.py": "98ca89ebb2de6a83ac8ecb5337a6277d66e6cdba98383fd4dcb3ed04ad0c6f8b",
    "domains/investment/__init__.py": "edb2ec092bf126a1e2a3c3005644dc65b3d8981ac6dd35cfa13a8154a5f464e8",
    "domains/investment/kernels.py": "7307034570bba9e7ed568eb442528ee4ffc885ab813c117130d3d89d09bbb1d0",
    "domains/investment/packets.py": "a455013a740e09c9a4a942b70e283c04af5dbb1eaeda2b17cfdcffc23150d6e5",
    "domains/investment/translator.py": "530941a4d9c7395f01c48cff8e9430d6c17623e7a7bbf661eccfca23c5f79d35",
    "domains/law.py": "aad52ffcc3eda77eed3a3ea7d8d07c79540ee6be23f24e4c7b0981d1c5bd6a36",
    "domains/medicine.py": "a1592abcb4aef02e2912eae6e0a2a4d91eb8d7d1e421aea5547cf811e8f14a41",
    "tests/__init__.py": "9a7e6e35013709b34c1e8ddf083e77aad0a7ff97965b99ba8b4fafc6686a7892",
    "tests/test_domain_independence.py": "ccd9d4ba25bec351fd9332064914546ff1976ec42e633a4b677c46c10600204e",
    "tests/test_freeze.py": "d9ed9ae3f1ff0dbfd761e277698a54c2757b76cc031ce6f507f5288b65e362ff",
    "tests/test_observability.py": "10d4f5aea1d4d1c191b11f7155c9d2f2f4442be7aa897f4672c3f443887f07a1",
    "tests/test_prototype.py": "45997e8440d5dff53d28a5442fbb977c8abb78d8c14129f29b1f26977970f76f",
}


@dataclass(frozen=True)
class FreezeReport:
    """The outcome of checking the freeze."""

    unchanged: tuple[str, ...]
    changed: tuple[str, ...]
    added: tuple[str, ...]
    removed: tuple[str, ...]
    current_digest: str
    pinned_digest: str

    @property
    def intact(self) -> bool:
        """True when nothing has moved since the freeze."""
        return not (self.changed or self.added or self.removed)


def verify_freeze() -> FreezeReport:
    """Compare the working tree against the pinned manifest."""
    states = current_state()
    by_path = {item.path: item.digest for item in states}

    unchanged: list[str] = []
    changed: list[str] = []
    for path, digest in sorted(by_path.items()):
        pinned = FROZEN_MANIFEST.get(path)
        if pinned is None:
            continue
        (unchanged if pinned == digest else changed).append(path)

    added = sorted(set(by_path) - set(FROZEN_MANIFEST))
    removed = sorted(set(FROZEN_MANIFEST) - set(by_path))

    return FreezeReport(
        unchanged=tuple(unchanged),
        changed=tuple(changed),
        added=tuple(added),
        removed=tuple(removed),
        current_digest=tree_digest(states),
        pinned_digest=FROZEN_TREE_DIGEST,
    )


def render_freeze() -> str:
    """Format the freeze verification for the terminal."""
    width = 78
    report = verify_freeze()
    lines = [
        "=" * width,
        f"CHOIR PROTOTYPE V{VERSION} -- {STATUS}",
        "=" * width,
        f"Files pinned    : {len(FROZEN_MANIFEST)}",
        f"Files present   : {len(report.unchanged) + len(report.changed) + len(report.added)}",
        "",
        f"Pinned tree digest  : {report.pinned_digest}",
        f"Current tree digest : {report.current_digest}",
        "",
        "-" * width,
    ]

    if report.intact:
        lines.append(
            "STATUS: INTACT -- the architecture is unchanged since the freeze."
        )
    else:
        lines.append("STATUS: MODIFIED -- the frozen architecture has moved.")
        for path in report.changed:
            lines.append(f"  changed : {path}")
        for path in report.added:
            lines.append(f"  added   : {path}")
        for path in report.removed:
            lines.append(f"  removed : {path}")
        lines.append("")
        lines.append(
            "If this was deliberate, bump the version and re-pin the manifest."
        )
        lines.append("If it was not, that is what this check exists to tell you.")

    lines.append("-" * width)
    lines.append("")
    lines.append("Python modules are pinned by normalised syntax tree, so the freeze")
    lines.append("survives reformatting and catches every change to an identifier,")
    lines.append("literal, docstring or statement. Other files are pinned by content.")
    lines.append("")
    lines.append("See FROZEN.md for what the freeze protects and what V0.2 may change.")
    return "\n".join(lines)
