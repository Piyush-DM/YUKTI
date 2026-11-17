# DAALE v0.1 Reference Implementation

DAALE is the **Deterministic Adversarial Analytical Logic Engine** used beneath YUKTI. This reference implementation is a narrow, auditable vertical slice for post-technical-due-diligence vendor approval.

It is not a chatbot and it does not ask a model to make the final decision.

## What the pipeline does

1. Validates the case and application policy.
2. Hashes the exact inputs.
3. Runs a bounded analyst pass.
4. Requires a complete evidence-to-claim relation matrix.
5. Runs an independent adversarial pass.
6. Validates every model-generated identifier.
7. Computes deterministic metrics from the validated findings.
8. Selects the first matching ordered policy rule.
9. Writes an immutable-style JSON audit trace with a unique filename.

The models classify and challenge evidence. The deterministic policy engine selects the policy state. A human institution retains final authority.

## Project structure

```text
daale_v0_1/
├── CHOIR_CONTRACT_DRAFT.md
├── README.md
├── requirements.txt
├── .env.example
├── run_daale.py
├── daale/
│   ├── client.py
│   ├── pipeline.py
│   ├── policy_engine.py
│   ├── prompts.py
│   ├── schemas.py
│   ├── trace.py
│   └── validation.py
├── cases/
├── policies/
├── fixtures/
└── tests/
```

## Windows setup

Open this folder in VS Code and run:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Put your OpenRouter API key in `.env` only when you want to run live inference. Never commit `.env`.

## Run offline first

Offline mode uses validated fixtures and makes no network request:

```powershell
.\.venv\Scripts\python.exe run_daale.py --offline
```

Expected policy state:

```text
REJECT
```

This result is produced because the fixture marks two critical requirements as `NOT_SATISFIED`, and no high-severity adversarial challenge disputes those findings.

## Run the tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The tests verify validation invariants, rule priority, conservative escalation, hold behavior, and successful advancement.

## Run with OpenRouter

After adding your key to `.env`:

```powershell
.\.venv\Scripts\python.exe run_daale.py --live
```

The default analyst and adversary models are both NVIDIA Nemotron 3 Ultra Free. They are separate inference passes but not independent model families. For stronger adversarial testing, configure different model slugs:

```env
DAALE_ANALYST_MODEL=your-analyst-model-slug
DAALE_ADVERSARY_MODEL=your-adversary-model-slug
DAALE_ANALYST_PROVIDER=your-analyst-provider-slug
DAALE_ADVERSARY_PROVIDER=your-adversary-provider-slug
```

Leave either provider value empty if you want OpenRouter to route that model across eligible providers.

If a selected model supports native JSON Schema output, set:

```env
OPENROUTER_NATIVE_JSON_SCHEMA=true
```

Keep it `false` for Nemotron 3 Ultra Free. DAALE will require JSON through the prompt and validate it locally.

## Decision-rule semantics

The policy contains an ordered list of rules. DAALE computes only declared metrics and selects the highest-priority matching rule. Supported operators are `eq`, `gte`, and `lte`.

No model confidence score is used. No weighted scoring formula is hidden in the engine.

### Combining the kernels' verdicts (decided 2026-11-09)

Several kernels may assess the same policy requirement. The engine combines them in one place, `aggregate_requirement_assessments` in `daale/policy_engine.py`:

- no kernel assessed it: `UNKNOWN`;
- every kernel that assessed it agrees: that verdict;
- they disagree: `UNKNOWN`, with each kernel's verdict recorded as `assessed_by` and `disagreement: true` in the requirement summary and in the gap report.

So a requirement is `SATISFIED` or `NOT_SATISFIED` only when the kernels that looked at it agree. A contested mandatory requirement becomes `UNKNOWN`, which the sample policy turns into a `HOLD` for a human. The result does not depend on kernel order. Every requirement in the policy appears in `requirement_summary`, assessed or not. (Before this, the last kernel in the fixed order silently won, and a requirement nobody assessed was missing from the summary.)

### What an incomplete run may conclude (decided 2026-11-09)

- If any kernel fails, the run is incomplete and always sets `requires_human_review`; `execution_integrity.human_review_reasons` says why.
- An incomplete run never emits `ADVANCE`. It becomes `ESCALATE` under the rule `INCOMPLETE-RUN-ADVANCE-BLOCKED`, and the policy's own result stays visible in `policy_state_before_integrity_check` and `other_matching_rule_ids`. `REJECT` and `HOLD` are conservative and are not blocked.
- A mandatory or critical requirement the kernels disagree on also sets `requires_human_review`.
- `degradation_mode` is `none` when nothing failed.

These rules live in `DaalePipeline._apply_integrity_rules`, the one place to change them. The flag travels in the decision packet, the trace and the API, and the D-Core gate acts on it: a flagged packet is escalated to `REVIEW_REQUIRED` instead of being committed (`docs/architecture/DECISION-005.md`, condition 3).

### Replay (DECISION-005, condition 2)

The policy state of a completed run is a deterministic function of the findings its trace recorded. To check that for any trace:

```powershell
python -m daale.replay runs/<trace>.json
```

It recomputes the decision from the recorded case, policy and findings and lists any field that differs. Exit status is 0 for a match, 1 for a difference and 2 for a refused run, which has no decision to recompute. Model calls are not replayed; they are what was recorded.

### Live check: do all six kernels run? (added 2026-11-09)

```powershell
python live_check.py              # one full judgment: six base kernels, the adversary, the decision, its replay
python live_check.py --base-only  # only the six base kernels, no adversary request; a few minutes faster
```

It makes real model calls, so the key must be in `.env` (`python set_key.py` enters it without showing it). It prints one row per kernel (result, calls made, tokens, and the reason for a failure) and then PASS or FAIL. Exit status 0 means all six base kernels succeeded and, in a full run, the adversary ran, nothing was refused and the decision replays identically from the recorded trace. Status 1 means a kernel or the adversary failed; status 2 means it could not start (no key, daily budget used up).

If every call seems to wait about three minutes before anything happens, the cause may be the network, not the provider. Google's address list starts with eight IPv6 addresses; where IPv6 does not work, each hangs about 21 s before the next is tried, so every new connection loses about 169 s before it falls back to IPv4. Set `DAALE_FORCE_IPV4=true` in `.env` to use IPv4 only (on the development machine this took listing the models from 169 s to 1.2 s). `live_check.py` tests for this and switches itself for that run, saying so. Set `LLM_NATIVE_JSON_SCHEMA=true` for Gemma on Google: without it CONTRARIAN spends its whole token budget on hidden reasoning and returns nothing (see `.env.example`). `tests/test_live_six_kernels.py` runs the same check as a test when `DAALE_LIVE=1` is set; the pass and fail logic itself is tested offline in `tests/test_live_check.py`.

## Trace files

Every run writes a new file under `runs/`. Filenames include the case ID, UTC time, and a random run ID, so model comparisons are never overwritten.

The trace includes:

- contract and engine versions;
- case and policy hashes;
- requested and served models;
- request IDs and token usage;
- analyst findings;
- adversarial findings;
- computed deterministic metrics;
- triggered policy rule;
- decision packet.

## Privacy warning

The included case is synthetic. Do not send confidential institutional evidence to a free model endpoint. Before using real organizational data, establish an approved provider, retention policy, access controls, secret management, and data-classification process.

## Current limitations

- CHOIR Contract Draft 0.1 is intentionally minimal and not a frozen canonical specification.
- The implementation covers one text-only decision workflow.
- It does not perform document ingestion, source authentication, calibrated uncertainty, retrieval, human review UI, or database persistence.
- Two passes using the same model are not fully independent adversarial review.
- The deterministic policy state is not the final institutional decision.
