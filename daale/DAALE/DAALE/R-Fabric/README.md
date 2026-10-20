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
