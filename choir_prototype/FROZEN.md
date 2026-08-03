# CHOIR Prototype — V0.1 FROZEN

**Status:** Frozen. Work continues in V0.2.

Verify the freeze:

```bash
python -m choir_prototype --frozen
```

---

## 1. What "frozen" means

Not the code as text — the **architecture**. Specifically:

| Frozen | Why |
|---|---|
| The seven pipeline stages and their order | Changing the order changes what can be explained |
| The IR shape (entities, claims, evidence, assumptions, relationships, uncertainty, metadata) | Everything downstream consumes only this |
| The kernel contract (`ChoirIR` → `Artifact`) | Kernel independence rests on it |
| Confidence derivation, and the rule that it is never authored | The result is meaningless if it can be typed in |
| The five decision rules and their ordering | Cross-domain identity (audit A6) rests on it |
| The core/domain boundary and its one-way dependency | The domain-independence claim rests on it |
| Renderers as pure projections of the record | Explanation faithfulness rests on it |
| Determinism: no clock, no randomness, no I/O, no concurrency | Replay rests on it |

The freeze is a **tripwire, not a prohibition**. V0.2 is expected to change things.
It exists so that changing the architecture is a deliberate act with a version bump
attached, rather than something that happens by accident.

---

## 2. How the freeze is enforced

Three independent mechanisms, all mechanical:

| Mechanism | Command | Catches |
|---|---|---|
| **Tree freeze** | `--frozen` | Any change to any file in the package |
| **Domain-independence audit** | `--audit` | Core/domain layering violations (A1–A7) |
| **Replay verification** | `--replay` | Loss of determinism or projection purity |
| **Test suite** | `python -m unittest discover -s choir_prototype -t .` | Every behavioural claim |

Python modules are pinned by **normalised syntax tree**, not raw bytes. The freeze
therefore survives a formatter pass and still catches every change to an identifier,
literal, docstring or statement. This distinction was learned the hard way: a byte-level
pin false-alarmed when `ruff format` reflowed one line during the portability experiment.

---

## 3. What V0.1 established

| Claim | Evidence |
|---|---|
| Independent kernels consume a canonical IR and produce structured reasoning | The pipeline runs; `TestKernelIndependence` |
| Execution is deterministic and replayable | `--replay`, four checks, all packets |
| Renderers cannot disagree with the reasoning | `projection-integrity` check |
| Confidence is derived, never authored | No code path accepts a literal; `TestDerivedConfidence` |
| The system can decline to conclude | `CONTESTED` and `INSUFFICIENT_BASIS` reached in multiple domains |
| Agreement between kernels is meaningful | Kernels cannot observe one another |
| **The core is domain-independent** | `--audit`: portability 1.00, four domains, hold-out control |

**100 tests** pass, of which 75 are the prototype's own.

The domain-independence result is the substantive one. Four domains — investment, law,
medicine, engineering — with different packet shapes and vocabularies share one core,
with **zero core changes**. Engineering was the hold-out: written after the core was
frozen and hash-pinned, as a control against the fix being tuned to the development set.

All five decision rules fire across the corpus, and two of them fire in more than one
domain. That is the strongest single piece of evidence that the reasoning is structural
rather than domain-tuned.

---

## 4. What V0.1 does **not** establish

Stated plainly, because the freeze should record limits as carefully as results.

| Gap | Consequence |
|---|---|
| **No defeat typing** | Falsifier F3 (graded vs structural defeat) cannot be tested at all. This is the single most likely route to a core change. |
| **No context lattice, no precedence ordering** | Conflicts are detected and reported, never adjudicated by principle |
| **No ambiguity representation** | The IR cannot hold an unresolved reading |
| **No provenance chain to source text** | Evidence cites a source label, not a locus in an edition |
| **Modality is a tag, not a logic** | Deontic depth untested; the likeliest gap for law |
| **All four domains are rule-interpretive with graded evidence** | A domain unlike these four is untested |
| **The prototype IR is a subset of the specified MIR** | Portability of the prototype core is evidence for, not proof of, portability of the full schema |

Four core docstrings still name investment as an illustrative example. Reported as a
non-blocking advisory by `--audit` rather than silently fixed: correcting the wording
would have changed the hashes and destroyed the hold-out evidence chain, and the evidence
is worth more than the prose.

---

## 5. Recommended V0.2 scope

In priority order, from the open questions the work itself surfaced:

1. **Defeat typing** — undercutting / rebutting / premise-denying, per
   `computational_primitives.md` §3.12. Unblocks the F3 falsifier, which is the highest-value
   open question in the whole programme.
2. **Conflict adjudication** — precedence principles and a context lattice, per
   `conflict_resolution.md` §5. Today conflicts are surfaced but never resolved.
3. **A fifth domain chosen to break the claim**, not to confirm it. Something quantitative
   or non-interpretive would test the boundary rather than pad the count.
4. **Provenance to source loci** — evidence that cites an edition and a locus, which is what
   the Vedic pipeline needs and what the investment domain currently fakes with labels.
5. **Ambiguity as a first-class IR citizen**, per
   `choir_intermediate_representation.md` §3.1.

Items 1 and 2 are the ones that would most likely force a core change. That is the point
of doing them next: the freeze makes the change visible.

---

## 6. Archive note

**This work is not committed to version control.** The git repository rooted at this
machine's home directory tracks none of it, and committing from here would sweep in
unrelated personal files. The freeze manifest in `freeze.py` is therefore the archival
record: it pins every file by content and reduces the whole state to one tree digest.

To place this under proper version control, initialise a repository at the project root
rather than the home directory:

```bash
git init C:/Users/PIYUSH/Desktop/YUKTI
```

Then commit, and tag as `v0.1`. Until that happens, `--frozen` is what tells you whether
the archived state is intact.
