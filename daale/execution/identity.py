"""Execution identity, bound to inputs rather than to what was emitted.

An execution needs a name before it produces anything, so that its trace, its
canonical writes and its provenance all hang off one identifier. How that
identifier is derived is not a detail -- it is the difference between an audit
trail that holds and one that quietly collides.

The lesson this module is built on
----------------------------------

``DECISION-006`` recorded a measured collision in the product layer: a figure
recorded as ``reported`` and the same figure recorded as ``estimated`` produced
an identical ``record_digest``, because the engine flattens both to
``Uncertainty.LIKELY`` and status appears nowhere else downstream. Two
materially different inputs, one hash. Anything keyed on that hash treated them
as the same event.

The general form of the defect: **an identifier derived from what a computation
emitted can collide when the computation does not observe part of its input.**
The fix is to derive identity from the input, at full fidelity, before anything
is discarded.

So the execution id here is computed over the package exactly as submitted --
every field, in recorded order -- and never over a result. Two executions
differing in any input byte are different executions, whether or not the
difference survives into their output. ``test_inputs_the_engine_would_flatten
_are_still_distinct_executions`` is the direct regression for the collision
above.

Order sensitivity is deliberate, for the same reason ``material.py`` gives:
identifiers downstream are positional, so a re-ordered package is a different
package. A normalised, order-insensitive digest would be coarser than the thing
it must be finer than.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping

# Versioned so the derivation can change without silently colliding with
# identifiers computed under an earlier rule.
EXECUTION_SCHEME = "daale-execution/1"


@dataclass(frozen=True)
class ExecutionIdentity:
    """What names one execution, and what it was derived from.

    ``input_digest`` is kept beside ``execution_id`` rather than folded away.
    An identifier nobody can re-derive is an assertion; one whose inputs are
    recorded next to it can be checked.
    """

    execution_id: str
    choir_version: str
    input_digest: str
    scheme: str = EXECUTION_SCHEME


def _canonical(payload: Any) -> str:
    """Reduce a package to one canonical string, preserving recorded order.

    ``sort_keys`` orders mapping *keys* so that two equal mappings written in a
    different key order agree -- Python dictionaries carry insertion order, and
    that is not part of what the institution recorded. Sequence order is left
    exactly as submitted, because it is.
    """
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def compute_input_digest(package: Mapping[str, Any]) -> str:
    """Hash a CHOIR package at full fidelity, before anything interprets it."""
    return hashlib.sha256(_canonical(package).encode("utf-8")).hexdigest()


def compute_execution_id(choir_version: str, input_digest: str) -> str:
    """Derive the execution identifier from the scheme, version and inputs.

    The CHOIR version participates: the same package executed under a different
    version of the theory is a different execution, and conflating the two
    would make a trace impossible to interpret later.
    """
    material = f"{EXECUTION_SCHEME}\n{choir_version}\n{input_digest}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


def identify(choir_version: str, package: Mapping[str, Any]) -> ExecutionIdentity:
    """Name an execution from its inputs alone."""
    input_digest = compute_input_digest(package)
    return ExecutionIdentity(
        execution_id=compute_execution_id(choir_version, input_digest),
        choir_version=choir_version,
        input_digest=input_digest,
    )
