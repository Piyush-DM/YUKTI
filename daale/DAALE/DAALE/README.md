# DAALE (this working copy)

Two components, evaluated and committed by different authorities, wired
together for the first time in this working copy on 2026-08-29:

- **`R-Fabric/`** — a copy of `D:\daale_v0_1`. An LLM-backed reference
  pipeline: base reasoning kernels run in parallel, an adversarial pass
  reviews their output, and a deterministic policy engine turns validated
  findings into a decision packet (`ADVANCE` / `HOLD` / `REJECT` /
  `ESCALATE`). Runs entirely on its own; see `R-Fabric/README.md`.
- **`D-Core/`** — a copy of `D:\YUKTI-1\daale` (the canonical, git-tracked
  monorepo's `daale/` package, past its v0 closure). A canonical control
  plane: validates, orders, versions, commits, traces. Deliberately built
  with no evaluator — see `D-Core/README.md` for the `DECISION-005` boundary
  that made that deliberate rather than incomplete.

## The `daale` junction

Both components' internal code imports itself as a top-level package named
`daale` (`from daale.execution import ...` in D-Core, `from daale.pipeline
import ...` in R-Fabric). They cannot both hold that name in one process, and
D-Core's folder here is named `D-Core`, not `daale`, so its own imports do not
resolve without help. `D:\DAALE\daale` is a Windows directory junction
pointing at `D-Core/` — non-destructive, and it is what lets D-Core's own
documented usage (`python -m daale conformance`, "run from the repository
directory") work unmodified from here. R-Fabric keeps its own separate
`daale/` package inside `R-Fabric/` and is never on the same `sys.path` as
D-Core's — see `run_pipeline.py` below for why that is a feature of this
integration, not a workaround.

One side effect: `python -m unittest` run from this directory discovers
D-Core's test suite twice (once as `D-Core.tests.*`, once as `daale.tests.*`,
through the junction) — same files, same results, doubled count. Harmless,
but if a clean count matters, name the suite explicitly:

```powershell
python -m unittest D-Core.tests.test_execution D-Core.tests.test_rfabric_bridge
```

## Running the integration

```powershell
python run_pipeline.py --offline
```

Runs R-Fabric's offline pipeline against the bundled vendor case, then offers
the resulting decision packet to the D-Core as a candidate. Prints R-Fabric's
decision packet, then the D-Core's gate checks, trace, and commit outcome.
Artifacts land under `R-Fabric/runs/` (R-Fabric's own trace) and
`reports/daale/rfabric_admission/` (the D-Core's admission record).

To offer an existing R-Fabric trace file without re-running the pipeline:

```powershell
python -m daale admit-rfabric R-Fabric/runs/<some-trace>.json
```

## What "work together" means here, and what it does not

See
[`docs/architecture/DECISION-005_RULING_rfabric_evaluates.md`](docs/architecture/DECISION-005_RULING_rfabric_evaluates.md)
for the full ruling this integration rests on. In short: **R-Fabric
evaluates; D-Core commits.** R-Fabric never gains write access to canonical
state, and D-Core never gains an evaluator — it only gained something able to
hand it a properly-shaped candidate, which `DETERMINISTIC_ORIGINS` was already
waiting for (`"rfabric"` was reserved there, and used as the test suite's
default candidate origin, before this integration produced a real one).

This does not make D-Core's conformance lock pass fully in this working
copy — that lock resolves citations against `choir/`, `choir_prototype/`, and
`docs/architecture/DECISION-00{1,2,3,4,6,7}*` files that live in `YUKTI-1` and
were not copied here. That gap predates this integration and is orthogonal to
it: the conformance lock and the execution/commit-gate machinery are
independent modules, and only the latter is exercised by
`run_pipeline.py` / `admit-rfabric`.
