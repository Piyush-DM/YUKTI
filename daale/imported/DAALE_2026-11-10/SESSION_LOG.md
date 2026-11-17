# YUKTI engine: session log and handoff

Sessions of 2026-11-08 to 2026-11-10. This file records everything done, in order, with the
current state, the decisions made, what was found, and what is still open. It contains no
secrets. Where a key matters, the file that holds it is named, never its value.

**Baseline: `daale/imported/DAALE_2026-11-10/`** (engine in `R-Fabric/`, committee core in `D-Core/`).
It is the engine from the user's `Downloads/DAALE_2026-11-08.zip`, adopted on 2026-11-10 (section 3.12).
Sections 3.1 to 3.11 describe the work done in the previous baseline, `daale/imported/_superseded/DAALE_2026-09-19/`,
which this one contains and extends. That older tree and the zip I built from it are archived in
`daale/imported/_superseded/`, not deleted.

---

## 1. Where things stand

| Area | State |
|---|---|
| Engine (R-Fabric pipeline) | Baseline is the 2026-11-09 build. Per its report, a **full live judgment passed**: six kernels on Gemma 4 31B plus the adversary on Gemini 3.8 Flash, REJECT on the sample case, in about 16 minutes. |
| Model setup | Direct Google key through the `generic` provider. Kernels on `gemma-4-31b-it`, adversary on `gemini-3.8-flash`. Per-model pacing and daily budgets. IPv4 forced, strict structured output on. |
| Decisions | DECISION-005 approved (option 1: R-Fabric evaluates, D-Core commits, four conditions). A failed kernel forces human review. Kernel disagreement resolves to UNKNOWN. |
| Intake | Built: user documents in, validated case out, no model involved. |
| HTTP API (`service/`) | Built, smoke-tested locally with a real client key. **Not deployed.** Its database and the portal key file were carried into the baseline. |
| Tests (run on 2026-11-10, offline, no key) | R-Fabric **226 passed, 1 skipped** (the opt-in live test). D-Core **106 passed, 1 failed**: `test_every_cited_evidence_still_exists` needs CHOIR files that exist only in the real repository. |
| Git | **Nothing committed.** Everything is untracked or modified in the working tree. The real repository does not have these changes. |
| Deployment | Planned only. No server, domain, HTTPS or portal exists yet. |
| Live ADVANCE | Achieved 2026-11-11 on DD-003 with every role on Gemini 3.8 Flash (section 3.17). |
| Investment (Aberdeen) test | Abandoned 2026-11-11 and archived under `cases/_abandoned_investment_2026-11-11/` (section 3.16). |

**Not independently confirmed by me:** the live pass and its numbers are from the 2026-11-09 report. I verified
the code and ran the offline suites; I did not run a live judgment on this baseline.
**Not proven at all:** anything with real client material; the API serving a live judgment; free-tier
reliability at five users.

---

---

## 2. What the project is (from the handoff the user pasted)

- **YUKTI**: Yielding Unified Knowledge Through Iteration. Structured reasoning for enterprise AI.
  Domain: yukti.agency. First application: investment committee and diligence workflows.
- **CHOIR** (Computational Heuristics for Ontological Institutional Reasoning): the theory.
  **DAALE** (Data Algorithmizing and Analytical Engine): the execution architecture. Names are canonical.
- Intended flow: structured input, normalised, several independent kernels, validated artifacts,
  synthesis, an inspectable judgment with provenance. Not one LLM simulating several voices.
- The handoff asked for: a working OpenRouter-compatible inference path on Gemma 4, a free VPS,
  an authenticated engine API (`/v1/...`), per-client credentials, and a separate client portal.
- Its success test: five users, hosted portal, submit a case, authenticated API, persisted
  structured judgment from Gemma 4.
- Constraints it set: inspect before changing; do not silently resolve open architecture decisions
  (DECISION-005); keep provider keys server-side; no shared unrestricted credential; do not assume
  free means unlimited; no large refactor.

---

## 3. Chronology

### 3.1 Inspection of the repository
- Branch `main`, commit `9348187`. Test suite: **310 passed** (Python 3.14.0 in `.venv`).
- **Gemma appeared nowhere in the repo.** The R-Fabric `.env` pointed at `anthropic/claude-3.5-sonnet`;
  the code default was a Nemotron free model.
- Two disconnected engines: the **workspace** (`applications/investment/workspace/`, deterministic CHOIR,
  no LLM calls, stdlib server, no auth, JSON-file `CaseStore`) and **R-Fabric** (the LLM pipeline, a CLI
  only, nested at `daale/DAALE/DAALE/`).
- `choir/openrouter api.txt` is **untracked and not gitignored** and held API keys. Two keys ended up
  displayed in this chat (one while redacting only one pattern, one inside a context document). **Both
  need rotating.**

### 3.2 The zip (`DAALE (1).zip`)
- Extracted safely into a scratch folder, nothing from it run there.
- Newer than the repo's nested copy: `pipeline.py` 669 lines against 505; unified finding schema;
  failure/recovery contract; three court-case corpora (Carlill, Donoghue, Hadley) with policies;
  traces to 2026-09-17. Not a superset: no workspace, website or CHOIR docs.
- Its `CONVERSATION_CONTEXT.md` documented a working-copy DECISION-005 ruling ("R-Fabric evaluates;
  D-Core commits"); the repo's `DECISION-005.md` still says **Open. Not accepted.**
- **Imported** into the repo as a new directory, `daale/imported/DAALE_2026-11-10/` (144 files). `.env`
  and caches excluded; keys redacted in two files. The old nested copy is untouched.
- Of the 22 recorded traces: 9 were served by offline fixtures, 13 were zero-call ESCALATE packets from
  failed attempts, **none were live**.

### 3.3 First prep
- `.env.example` (API slot empty), `preflight.py` (exit 0 ready, 2 engine ready but live not
  configured, 1 broken), `setup_env.ps1`.
- The user clarified the earlier engine was a showcase engine for a product video, then asked to prepare
  it for live work and to make sure nothing returns fixed output.

### 3.4 Audit of the engine, and fixes
Defects found and fixed (each has a test that fails on the old code where the code was the cause):

| Defect | Fix |
|---|---|
| Every successful kernel was called **twice** (once to run it, once to fetch its record). | Record and messages kept from the validated call. |
| Live runs **skipped the adversary silently** (the pipeline probed the client for an `outputs` attribute only the fixture client has). | Adversary runs for every non-fixture client; `FixtureClient.is_fixture` marks the exception. |
| Adversary prompt demanded relation findings its own validator rejects. | Prompt corrected. |
| A failed adversary was recorded as "no findings", so an unchallenged decision could ADVANCE. | Failed adversary now produces an ESCALATE refusal (`DEGRADED-EXECUTION`). |
| `adversarial_summary` always empty (read a field that no longer exists). | Reads `summary`. |
| `pipeline_steps` hardcoded to "completed". | Derived from what ran. |
| `degradation_mode` could never leave "retry" (string comparison ordered `retry` above `abort`). | Explicit severity order. |
| A 429 was classified as a crash, so rate-limit backoff never applied. | `DaaleModelError.status_code`, classification by status. |
| Model-output validation errors aborted the whole run. | Retry then degrade, per the execution contract. |
| Which kernel's verdict won depended on thread timing. | Outputs assembled in fixed kernel order. |
| Hardcoded Nemotron default model. | No model is assumed; `--live` refuses without one. |
| Prompts quoted "2 claims x 3 evidence". | Each prompt states the case's real IDs and relation count. |
| D-Core bridge read an old analyst format, so admitted packages cited no evidence. | Reads the unified format and the old one. |

Test change worth knowing: `test_incomplete_evidence_matrix_is_rejected` now expects an ESCALATE
refusal instead of an exception. The decision packet now carries `execution_integrity`.

### 3.5 Intake (`daale/intake.py`)
Deterministic, no model. A manifest gives the decision question, the user's claims, and documents
(`.txt`/`.md`, by `path` or inline `text`). Output: a schema-valid case with evidence cut at paragraph
boundaries (each an exact substring), line ranges, nearest Markdown heading, SHA-256 of the exact bytes,
IDs in manifest order. Never invents claims, pages or dates. Refuses PDF/Word, binary or empty files,
paths outside the manifest, unknown fields, and more than 30 evidence items (every kernel must rate every
claim against every item). `allow_paths=False` for outside input. `verify_provenance` re-checks later.
Tool: `python -m daale.intake manifest.json --out case.json`; `run_daale.py --live --material manifest.json`.

### 3.6 Providers
- Pipeline is provider-agnostic (needs only `complete_json(purpose, model, messages, schema)`).
  `OpenRouterClient` is OpenRouter-specific; clients for NVIDIA and AIML also existed.
- Added `GenericApiClient` (provider `generic`, env `LLM_*`): any chat-completions endpoint, called
  directly. Key sent only over https (or loopback). Prompted JSON plus local validation. Strips inline
  `<thought>...</thought>` reasoning blocks (Gemma 4 does this). Detects `finish_reason: length`.
- Provider and model setup moved into `daale/providers.py`, shared by the CLI and the API.
- Renamed once on request from `openai_compat`/`OPENAI_COMPAT_*` to `generic`/`LLM_*`.
- `check_provider.py`: lists models and makes one tiny completion, prints no secrets.

### 3.7 First contact with Google, and live runs
- Base URL that worked: `https://generativelanguage.googleapis.com/v1beta/openai`. Model list showed 61
  models; Gemma 4 IDs are `gemma-4-31b-it` and `gemma-4-26b-a4b-it` (so the handoff's "20B" is really
  26B A4B). The short ID form works.
- Run 1 (Gemma 4 31B, no pacing): stalled with no output; stopped after about 15 minutes.
- Progress logging added (`daale.pipeline`, `daale.client` loggers, to stderr).
- Run 2 (`gemini-3.8-flash` for everything): 6 of 6 base kernels succeeded (about 42.7k tokens), no rate
  limit errors; calls took 100 to 250 s each (reasoning), with two 180 s read timeouts; the adversary
  returned malformed JSON twice, so the engine refused to decide (ESCALATE, degraded).
- A replay of the adversary call parsed fine (843 completion tokens), so the failure is intermittent,
  not truncation. Changes: JSON errors now report position and context; MALFORMED_JSON retries 2 to 3;
  default timeout 180 s to 600 s.
- Run 3 was stopped when the user hit the per-minute cap.

### 3.8 Quotas, pacing, budgets
The user's limits (confirmed against an AI Studio screenshot):

| Model | Requests/min | Tokens/min | Requests/day |
|---|---|---|---|
| Gemini 3.8 Flash | 5 | 250K | 20 |
| Gemma 4 31B | 30 | **16K** | 14,400 |

- `RequestPacer`: every HTTP attempt, retries included, waits for room under the per-minute request
  and token caps. Tokens are reserved from an estimate (prompt at about 3.5 chars per token plus
  `LLM_EXPECTED_OUTPUT_TOKENS`) and corrected to the provider's reported total.
- `RequestBudget`: daily request count on disk, rolls over at midnight Pacific. A judgment is refused
  before any request if a model's remaining budget cannot cover the kernels assigned to it. The API
  returns 429 with Retry-After in that case.
- `ModelPacers`: all of this kept **per model**. Config: `LLM_LIMITS=model=rpm/rpd/tpm;...`.
- An exhausted quota and a truncated reply are classified as non-retryable.
- The 500 and 503 errors in the second Gemma attempt coincided with the Gemma token cap being exceeded
  (26K of 16K in the dashboard). With token pacing in place the errors were fewer but still occurred.
- Gemma's 16K tokens/min caps case size: roughly 30,000 characters of case text per request, less in
  practice because output grows with claims times evidence.

### 3.9 First complete live judgment (Gemma kernels, Gemini adversary)
- Duration 13 minutes. Result **REJECT**, rule `P080-CRITICAL-FAILURE`: R1 and R2 NOT_SATISFIED,
  R3 and R4 UNKNOWN, C1 and C2 CONTRADICTED. Matches the offline fixture's decision for the same case.
- 4 of 6 base kernels succeeded (ANALYST, FIRST_PRINCIPLES, EXPANSIONIST, HISTORIAN: 26,685 tokens).
  CONTRARIAN was cut off at 8,000 tokens twice; OUTSIDER put a requirement verdict in a CHALLENGE status
  field twice (same wrong answer, because retries at temperature 0 repeat). Adversary on Gemini: 173 s,
  18,569 tokens, no high-severity challenge.
- Changes afterwards: a rejected reply is sent back with the validation error and a request to correct it;
  truncated replies are not retried; `LLM_MAX_TOKENS` raised to 12000 in the user's `.env`.
- Gemini budget after this run: **18 of 20 used** for 2026-11-08 (Pacific).

### 3.10 The HTTP API (`service/`)
FastAPI, SQLite, no external services. `uvicorn "service.app:create_app_from_env" --factory`.

| Endpoint | Purpose |
|---|---|
| `GET /v1/health` (open) | status, provider, model, policy ids |
| `POST /v1/judgments` | 202 with an id; body has `policy_id` and either `case` or `material` (inline documents) |
| `GET /v1/judgments`, `/v1/judgments/{id}` | list; status and decision (`degraded` flag) |
| `GET /v1/judgments/{id}/audit` | full trace: case, prompts, calls, findings, gap report |
| `GET /v1/cases`, `/v1/cases/{case_id}` | judgments grouped by case id |
| `GET /v1/usage` | judgments, model calls, tokens |

- Keys: `yk_live_...`, 256 random bits, only a SHA-256 stored, revocable per key, client disable,
  managed locally with `python -m service.manage_keys` (no HTTP admin).
- Isolation: every query is scoped to the caller's client; another client gets 404.
- Limits: 60 requests/min per key, 2 active judgments per client, 1 running server-wide, 500 KB bodies;
  file paths in `material` refused. Results persist; jobs left running by a restart are marked failed.
- Created client "YUKTI Portal" (`cl_c7b76078cc77`) and issued key `key_9d6e01af77` to the gitignored
  file `secrets/portal.key`. Verified against a locally running server: no key 401, wrong key 401,
  valid key 200. The server was then stopped.

### 3.11 Deployment research (not acted on)
- Google Cloud trial: $300 credit, 90 days or until used; India needs an INR billing account.
- Oracle Always Free: only $0-forever candidate; ARM capacity often unavailable; sources disagree on
  the allowance; strict card checks.
- Cloudflare Pages free: 500 builds a month, unlimited static traffic; commercial-use terms not confirmed.
- Concerns flagged: Google's free tier may use prompts to improve its products (**recalled, not
  confirmed; check before real client data**); the engine key must live in a server-side forwarder, not
  browser JavaScript; the portal has no user login or frontend yet.

### 3.12 Adopting the 2026-11-09 engine (2026-11-10)
The user supplied `Downloads/DAALE_2026-11-08.zip`, a newer build produced in another session from a working
copy on `D:\DAALE_2026-11-08\DAALE` (a snapshot, not a git repository).

- **Compared with the previous baseline:** 125 files identical, 19 changed, 17 new, none missing, so it is a
  strict superset of the work above. Its own `SESSION_REPORT_2026-11-09.md` is kept in the baseline root.
- **Imported** as a new directory without its `.env`, `data/`, `runs/` and caches; every file scanned for
  key-shaped text first (none found). The zip itself contains a live `.env`; do not share it as it is.
- **Reviewed before running:** `network.py`, `set_key.py`, the opt-in live test.
- **Tests:** see section 1. The report's numbers (167 passed excluding the service, 107 for D-Core) match
  what I measured, allowing for the 25 service tests and the one repo-dependent D-Core test.
- **Configuration:** a `.env` was created for the baseline from the previous one plus the report's four
  settings. The service database (1 client, 1 key) and the portal key file were copied across.

What the report says changed (a different session did this work):

| Problem | Cause and fix |
|---|---|
| Every live call lost about **169 s** | Google's hostname resolves to eight IPv6 addresses first, IPv6 does not work on the user's network, and each hung about 21 s. `DAALE_FORCE_IPV4=true` and `daale/network.py`; `live_check.py` detects and switches itself. |
| CONTRARIAN failed | Not the length limit: Gemma 4 spent its whole budget on hidden reasoning (a loop) and returned no answer. Fix: strict structured output (`LLM_NATIVE_JSON_SCHEMA=true`); the same call then answered in 1,749 tokens. |
| OUTSIDER failed twice identically | The retry was blind: the rejected reply never reached the model. The rejected reply is now attached, the repair message names each finding and the fix, and prompts say to use `GENERAL` for whole-case findings. |
| One stalled call cost 3 x 500 s | A read timeout was retried at both the HTTP and kernel layers. The HTTP layer no longer retries it. |
| "Last kernel wins" for requirement verdicts | Unanimity: a requirement is SATISFIED or NOT_SATISFIED only if every kernel that assessed it agrees, else UNKNOWN; unassessed ones are UNKNOWN and listed. |
| Bridge labelled every unsatisfied requirement WEAKENS | SATISFIED to SUPPORTS, NOT_SATISFIED to CONTRADICTS, UNKNOWN to CONTEXTUAL. |
| Clean run reported degradation mode `retry` | Now `none`. |

New in the baseline: `daale/replay.py` (`python -m daale.replay <trace>` recomputes a decision from its
recorded findings), `live_check.py` (full judgment, decision, replay), `set_key.py` (hidden prompt, writes the
key to `.env` without showing it), `daale/network.py`, D-Core `Candidate.needs_review` and a `REVIEW_REQUIRED`
path in the commit gate, and tests for each.

Decisions recorded by that session (the user chose option 1):
- **DECISION-005, approved 2026-11-09:** R-Fabric evaluates, D-Core commits. Conditions: DECISION-001 narrowed
  (model kernels give advisory, replayable findings; only deterministic code decides); the replay command;
  a packet flagged for human review goes to `REVIEW_REQUIRED` instead of being committed; the authority
  notice stays. Full ADR in `docs/architecture/DECISION-005.md`, options in `BRIEF-DECISION-005_2026-11-09.md`.
- **Any failed kernel forces human review.** An incomplete run never emits ADVANCE; it becomes ESCALATE under
  `INCOMPLETE-RUN-ADVANCE-BLOCKED`, with the policy's own result still visible in the packet.
- **Kernel disagreement:** unanimity, otherwise UNKNOWN.

Reported live evidence (not re-run by me): the passing `live_check.py` run took 15 min 57 s; the Gemma servers
answered 503 or 500 sixteen times in it (four of six kernels needed a second attempt); both full runs an hour
apart produced byte-identical kernel outputs; Gemini used 6 of 20 requests and Gemma 53 of 14,400 that day.

---

### 3.13 Blind test on a case that should be accepted, and the resume (2026-11-10)
- **Case:** `cases/vendor_beta.json` ("Vendor Beta", decision id DD-002): same policy and claims as the sample
  case, five evidence items, four of which state that each document the policy requires was supplied. Correct
  answer under the policy: ADVANCE. The expected outcome was written to `cases/expected/vendor_beta.expected.json`
  **before** the case existed or ran; the engine never reads that folder; the case text contains no outcome words.
  (The fingerprint printed at the time was of the text with LF line endings; the file on disk has CRLF. With
  line endings normalised the hash matches, so the file is unchanged. The fingerprint should have been taken
  from the stored bytes.) Limit: I wrote the case knowing the policy, so this tests whether the engine reaches the
  intended answer unprompted, not whether an independent author agrees.
- **Result:** inconclusive. The engine returned a degraded ESCALATE: the Gemini adversary failed (a 503, then
  two 500-second read timeouts) and OUTSIDER failed three times on a parser bug. The five surviving kernels
  independently rated R1 to R4 SATISFIED and C1 SUPPORTED, matching the expected ADVANCE. That is evidence about
  the kernels, not a decision.
- **Parser fix:** a complete JSON object followed only by a stray closing code fence is now accepted (other
  trailing text still fails). Seen live in OUTSIDER's reply.
- **Resume (`DaalePipeline.resume`, `run_daale.py --resume <trace>`):** finishes an incomplete run by running again
  only the failed base kernels and the adversary (always, since it either failed or saw base outputs that are
  being replaced). Kernels that succeeded are reused exactly as recorded: the output and prompt hashes are
  checked (a mismatch refuses the whole resume before any request) and the output is validated again. Case and
  policy come from the trace, so a resume cannot be pointed at different material. The request budget is checked
  for only what will be sent. The new trace carries `resumed_from` (the prior run id, a hash of the prior trace,
  what was reused and what ran again), the earlier failed attempts stay in the audit events, and reused model calls
  are marked `reused_from_run` so tokens are not counted twice. A resumed trace replays to the same decision.
  Verified offline: 15 tests, including tamper cases and mutation checks (breaking reuse fails 6 of them; skipping
  the hash check fails 2). A dry plan against the real DD-002 trace reuses 5 kernels and would send OUTSIDER to
  Gemma and the adversary to Gemini. Suite: 209 passed, 1 skipped.

---

- **Live resume of DD-002 (completed):** reused the five good kernels, ran OUTSIDER (Gemma, ok on its first attempt
  after one 503, 5,291 tokens) and the adversary (Gemini, ok on its first attempt, 388 s, 19,770 tokens). 25,061
  tokens and 2 to 3 requests instead of a full run's 7. Replay recomputed the decision identically.
- **Outcome: ESCALATE (rule `P100-HIGH-CHALLENGE`), not the pre-registered ADVANCE. This is a miss against the
  registered expectation.** All four requirements came out SATISFIED (unanimous, 40 supporting relations, no
  weakening or contradicting ones), C1 and C2 SUPPORTED, no failed kernels, no human review flag. The adversary
  raised one HIGH challenge on **C2** ("risk profile is acceptable for final approval"): UNSUPPORTED, because the
  supplied assurance documents show technical verification but no stated organizational risk threshold or formal
  risk acceptance. Rule P100 (any HIGH challenge) outranks P050 (all mandatory satisfied), so the policy escalates.
- **Reading of the miss, not an excuse for it:** the expectation I registered considered only the four requirements.
  The case never contained evidence that anyone accepted the residual risk (its only C2-related evidence was
  revenue growth and an 18 percent customer concentration), so the adversary's objection is defensible. The
  weakness is in the case design (claim C2 had no direct evidence) and in the policy (an adversarial HIGH
  challenge always escalates), not clearly in the engine. The registered expectation stands as recorded; the case
  and its expected outcome were not edited afterwards.
- **What it shows:** the engine is conservative: with every requirement met it still sent the case to a person
  over an unsupported claim. It also shows the pipeline produces different decisions for different cases (REJECT for
  the weak case, ESCALATE for this one); it has not yet produced an ADVANCE, so that path is untested live.

### 3.14 Second vendor case (DD-003) and the investment cases from the Aberdeen page (2026-11-10)
- **DD-003 ("Vendor Gamma"), registered expectation ADVANCE:** same policy and claims, six evidence items including
  the risk committee's recorded acceptance of the residual risks. Written after the DD-002 result, which is
  disclosed in its registered file. **Result: ESCALATE (`INCOMPLETE-RUN-ADVANCE-BLOCKED`), a miss on the registered
  scoring.** The reasoning matched the expectation in every detail: all five surviving kernels rated R1 to R4
  SATISFIED, C1 and C2 SUPPORTED, 37 supporting relations, none weakening or contradicting, and the Gemini
  adversary found nothing to challenge (0 findings). The policy's own state was ADVANCE (rule P050); the packet
  records `policy_state_before_integrity_check: ADVANCE`. The decision was blocked because HISTORIAN's reply was
  cut off at the 16,000-token ceiling after 541 s (a reasoning loop; not retried, by rule), which made the run
  incomplete, and an incomplete run can never ADVANCE. The adversary took two attempts (a 503, then 436 s). So the
  ADVANCE path works in the engine's logic but has not yet produced a complete live ADVANCE. A `--resume` of this
  trace (HISTORIAN and the adversary, 1 Gemma and at least 1 Gemini request) is the obvious next step.
- **Aberdeen cases:** the user supplied `aberdeeninvestments.com/.../investment-case-studies` (eight holdings of an
  India-focused trust, each a "why do we like the investment" note). Marketing write-ups of holdings, not decision
  records, all favourable, so "the trust holds it" is a weak label. Built from ICICI Bank and Aegis Logistics, facts
  paraphrased and the company anonymised: `inv_bank_a`, `inv_logistics_a` (as published) and `inv_bank_b`,
  `inv_logistics_b` (one requirement's evidence replaced with invented adverse facts: financial strength for the
  bank, management and controls for the logistics company). The pairs test whether the decision follows the
  evidence rather than the company's reputation. Policy `INVESTMENT-QUALITY-SCREEN` (R1 competitive position, R2
  financial strength, R3 management and governance, all critical; R4 sustainability, mandatory but not critical; a
  failed critical requirement outranks an adversarial escalation) is **my draft and needs the user's sign-off**.
  Expected: A cases ADVANCE, B cases REJECT (R2 and R3 respectively). Registered before the cases existed.
  A runner (`run_inv_suite.py` in the session scratch folder) runs them one at a time and scores them;
  results were pending when this was written. An earlier attempt to use a legal case guide was dropped at the
  user's request.

---

### 3.15 The investment suite's result, and the resilience fixes (2026-11-10 and 11)
- **Result of the four Aberdeen-derived cases (run once, old code):** 0 of 4 final decisions matched, but the substance
  held in both cases that produced a trace.
  - `inv_bank_a` (expected ADVANCE): final ESCALATE (`INCOMPLETE-RUN-ADVANCE-BLOCKED`); the policy's own state was
    ADVANCE. ANALYST, OUTSIDER and HISTORIAN rated R1 to R4 SATISFIED, CONTRARIAN returned no requirement verdicts,
    FIRST_PRINCIPLES and EXPANSIONIST failed, and the adversary raised only two MEDIUM challenges (C3 ambiguous, R4
    omitted evidence), so nothing escalated on challenge.
  - `inv_bank_b` (expected REJECT via R2): final ESCALATE (`DEGRADED-EXECUTION`): the adversary failed (Gemini 503s,
    then the daily budget ran out) and EXPANSIONIST failed. All five kernels that finished rated **R2 NOT_SATISFIED**,
    the intended failure. They also rated **R3 NOT_SATISFIED**, which I did not intend: my reversal also removed the
    sentence about how the bank handled earlier stress, so R3's evidence was thinner than "one requirement flipped".
    With a capital breach and rising bad loans that inference is defensible; the case design was at fault. A failed
    critical requirement would reject under the policy, but that was not measured because the run was degraded.
  - `inv_logistics_a` and `inv_logistics_b`: refused up front (Gemini budget counter at 0), nothing sent.
- **Fixes made (226 tests pass, 1 skipped; mutation checks: disabling the fallback fails 6 of the 17 new tests,
  removing the nudge fails 1):**
  - A **truncated** reply is retried **once with a nudge** ("reason briefly, then return the JSON now") instead of
    never; with a fallback model configured it goes straight to the fallback, since the same model tends to loop again.
  - The repair message now **names the target_type rule** ("an EVIDENCE_RELATION is about a claim: target_type
    'CLAIM', target_id such as C1; never POLICY or GENERAL"), which FIRST_PRINCIPLES broke three times.
  - **Fallback models** (`DAALE_FALLBACK_MODEL`, per kernel `DAALE_<KERNEL>_FALLBACK_MODEL`): tried once for a kernel
    or the adversary after the primary fails in a way another model might not share (5xx, timeout, exhausted daily
    budget, truncation, unusable output). Not used for failures any model would share (a bad case). A primary with
    a fallback waiting gets at most two attempts, so minutes are not burned on a failing model. The budget check lets
    kernels a model cannot take spill onto their fallback. Every fallback is recorded in the audit events and listed
    in `execution_integrity.fallbacks_used`, and the trace shows which model produced each finding.
  - `DAALE_FALLBACK_MODEL=gemma-4-26b-a4b-it` is set in the user's `.env`. Its rate limits are not known, so it runs
    unpaced until `LLM_LIMITS` has an entry. It is the same family as the kernels, so an adversary that falls back
    to it is less independent than one on Gemini; that is recorded, not prevented.
- **Open question:** the budget counter counts every HTTP attempt, including 503s, and Gemini's 20 requests a day ran
  out mid-suite. AI Studio showed Gemma at 0 requests used after a run of 5xx errors, which suggests failed requests
  do not count against the provider's daily quota. If that holds for Gemini, the counter is too conservative.
  Check on AI Studio before changing it.

---

### 3.16 The investment test is abandoned (2026-11-11)
- **Decision (the user's):** stop the Aberdeen-derived investment test and clean up. The resume of the two bank cases
  was stopped mid-run (runner and engine processes ended; none remain). Nothing was left half-written: traces are
  written only at the end of a run.
- **Moved, not deleted, into `R-Fabric/cases/_abandoned_investment_2026-11-11/`:** the four cases, their four
  registered expectation files, and the draft `INVESTMENT-QUALITY-SCREEN` policy (so the API no longer lists it).
  Their traces from the first runs stay in `runs/` (gitignored). The registered expectations are kept as they were
  written, so the record of what was predicted before the runs is intact. Deleting the archive is one command.
- **Result of the abandoned test, final:** inconclusive. First run: 0 of 4 final decisions matched, for
  infrastructure reasons (failed kernels, the Gemini daily budget exhausted by 503 retries, two cases refused up
  front). The substance held where traces exist (see 3.15). The resume attempt, cut off at 16:31, showed the
  fixes below do not cure the underlying problem.
- **What the resume attempt showed (the one new finding):** with the nudge, the target_type hint and a Gemma 26B fallback
  all active, FIRST_PRINCIPLES still failed (503, then the same `'POLICY'` target_type slip, then truncation twice on
  the fallback) and EXPANSIONIST was truncated on both the 31B and the 26B model. Gemma 4 loops in its reasoning on
  some kernel prompts regardless of those mitigations; across all runs five kernel attempts hit the 16,000-token
  ceiling (CONTRARIAN, HISTORIAN, EXPANSIONIST twice, FIRST_PRINCIPLES). Gemini Flash completed all six kernels with
  no truncation in an earlier run. A zero-cost mitigation that needs no code: assign the loop-prone kernels to
  `gemini-3.8-flash` with `DAALE_<KERNEL>_MODEL` (all six would cost 7 of the 20 daily Gemini requests per judgment).
- **Budget constraint stated by the user:** no money to spend on testing; funds are reserved for the VPS and for working
  credentials. The VPS can be covered by the Google Cloud trial credit or Oracle's free tier, so the open spending
  question is inference. A hard daily token cap per model, so that a paid key cannot overspend, was proposed and not
  yet built. A switch to Kimi or GLM was discussed and deferred (client data would go to Chinese providers; structured
  output unconfirmed for both; free access through NVIDIA's hosted endpoints is unverified).
- **State at the time of writing:** no engine processes running; nothing committed; tests unchanged (226 passed, 1 skipped);
  the fallback model setting (`DAALE_FALLBACK_MODEL=gemma-4-26b-a4b-it`) remains in the user's `.env`, though it did not
  help on the looping kernels.

---

### 3.17 First complete live ADVANCE (2026-11-11)
- **Priming:** counters reconciled with the AI Studio screenshot (Gemini 0 of 20, Gemma 31B and 26B 5 each); the Gemma 26B
  limits (30 per minute, 14,400 per day, 16K tokens per minute) added to `LLM_LIMITS`; a launcher `run_profile.py` and a
  non-secret profile `profiles/test_gemini.env` (every kernel and the adversary on `gemini-3.8-flash`, fallback
  `gemma-4-31b-it`). The profile is laid over `.env`, so the key and the user's own settings are untouched. A profile is
  refused if it contains anything secret-looking.
  Command: `python run_profile.py profiles/test_gemini.env --live --case cases/vendor_gamma.json`.
- **Run (DD-003 again, registered expectation ADVANCE, file unchanged):** **ADVANCE, rule `P050-ALL-MANDATORY-SATISFIED`,
  a match** on the decision, all four requirements SATISFIED and both claims SUPPORTED. All six base kernels succeeded
  (OUTSIDER needed a second attempt after a 503), the adversary ran on its first attempt and raised one MEDIUM
  challenge on C2 (the risk committee's tier-2 threshold is not backed by evidence of the vendor's assigned tier), so
  nothing escalated. 41 supporting relations, 3 weakening, 0 contradicting. No fallback was used, no human review was
  required, degradation mode `none`, and replay recomputed ADVANCE identically from the recorded findings.
- **Speed and size:** 3 min 49 s end to end (against 15 to 30 minutes on Gemma 4), 7 model calls and 66,822 tokens, all
  served by Gemini. This is the first live ADVANCE the engine has produced that was not blocked by an incomplete run.
- **Caveats:** one run on one case; the same case as the earlier Gemma run (so a second sample, not a blind first one,
  and the case was written after DD-002); every role on one model family, which gives up the independence between the
  kernels and the adversary that the design prefers; written by the person who knows the policy. Gemini's 20 requests a
  day limit this to a few judgments a day. The engine's counter shows 14 of 20 used after this run (it counts every HTTP
  attempt, including 503 retries); AI Studio's own figure is probably lower, since failed requests appear not to count
  against the daily quota. Check AI Studio before trusting the counter.
- **What it changes:** the engine's whole path (intake-built case, parallel kernels, adversary, deterministic policy,
  integrity rules, replay) now has a complete live pass on both REJECT (vendor_alpha) and ADVANCE (vendor_gamma). Gemma 4 on
  the free tier, not the architecture, was the reliability problem.

---

### 3.18 The investment suite on the Google split, and the adversary veto is kept (2026-11-11 and 12)
- **Setup:** the four Aberdeen-derived cases were restored to `cases/` and run one at a time against their unedited
  registered expectations. Models: `gemini-3-flash-preview` for FIRST_PRINCIPLES, EXPANSIONIST, CONTRARIAN and the
  adversary; `gemini-2.5-flash` for ANALYST, OUTSIDER and HISTORIAN; each is the other's fallback
  (`profiles/test_google.env`). An earlier attempt on Gemma 4 alone (31B and 26B) gave 0 of 4, all for
  infrastructure reasons (truncation, validation slips, 500 and 503 errors, calls hung for up to two hours).
- **Result under policy v0.1 (the baseline): 2 of 4 decisions matched.** Every run was complete (no failed kernel)
  and every replay recomputed the decision identically.

  | Case | Expected | Got | Rule |
  |---|---|---|---|
  | `inv_bank_a` | ADVANCE | ESCALATE (miss) | `IQS090-HIGH-CHALLENGE` |
  | `inv_bank_b2` | REJECT via R2 | REJECT, R2 NOT_SATISFIED (match) | `IQS100-CRITICAL-FAILURE` |
  | `inv_logistics_a` | ADVANCE | ESCALATE (miss) | `IQS090-HIGH-CHALLENGE` |
  | `inv_logistics_b` | REJECT via R3 | REJECT, R3 and also R2 NOT_SATISFIED (match on the decision) | `IQS100-CRITICAL-FAILURE` |

- **Why the two ADVANCE cases missed:** in `inv_bank_a` all four requirements were SATISFIED by every kernel, and the
  adversary raised one HIGH challenge (R3: E4 states the outcome of past stress without the actions taken). In
  `inv_logistics_a` the adversary raised three HIGH findings, and CONTRARIAN answered UNKNOWN on R2 and R3 against
  four SATISFIED, which the unanimous rule turned into UNKNOWN. No false ADVANCE occurred in any run.
- **Changes made on 2026-11-12 to try to match:**
  1. `requirement_aggregation: unanimous_definite`, opt-in per policy (`policy_engine.py`, `schemas.py`): UNKNOWN is an
     abstention; SATISFIED against NOT_SATISFIED is still UNKNOWN; a verdict needs more kernels deciding than
     abstaining. Policies without the field keep the unanimous rule.
  2. `policies/investment_quality_screen_v0_2.json`: v0.1's rules plus that aggregation mode. v0.1 is unchanged.
  3. The adversary's severity wording (`prompts.py`): HIGH only when a kernel's finding is wrong; "the evidence is a
     summary or lacks detail" is MEDIUM at most; a CONTRADICTION needs two evidence items with incompatible facts.
     This applies to every policy.
  4. Five tests for the new mode. Suite: 231 passed, 1 skipped.
- **What the changes did:** replaying the stored findings under v0.2 turns `inv_logistics_a`'s R2 and R3 to SATISFIED
  and keeps both REJECT cases at REJECT. The live rerun of `inv_bank_a` under v0.2 with the new wording was still
  ESCALATE: all requirements SATISFIED, three HIGH adversary challenges (R1, R3, R4), up from one. One sample, so the
  wording change has shown no benefit. `inv_logistics_a` was not rerun: 503 retries on `gemini-2.5-flash` used the
  rest of that day's 20 requests.
- **Decision (the user's, 2026-11-12): keep the veto.** A single HIGH adversary finding still escalates to a human.
  The alternative, making the adversary advisory in v0.2, would have matched 4 of 4 on the stored findings by fitting
  the policy to four cases whose answers were written by the policy's author, and was rejected.
- **How the result is recorded:** on thin, one-source evidence the engine escalates rather than advances, and it
  rejects where the evidence is adverse. The ADVANCE expectations for these two cases may themselves be too
  generous: the bank evidence mentions "earlier governance concerns" with no detail, and the logistics evidence the
  death of a "pivotal" leader. ADVANCE on this policy is still untested with fuller evidence; that needs new cases
  with expectations registered before they run.

---

---

## 4. Current configuration (non-secret)

`R-Fabric/.env` (gitignored) holds:
- `DAALE_LIVE_PROVIDER=generic`
- `LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai`; `LLM_API_KEY` (secret, set)
- `DAALE_DEFAULT_MODEL=gemma-4-31b-it`; `DAALE_ADVERSARY_MODEL=gemini-3.8-flash`
- `LLM_LIMITS=gemini-3.8-flash=5/20/250k;gemma-4-31b-it=30/14400/16k` (requests per minute / per day / tokens per minute)
- `LLM_MAX_TOKENS=16000`, `LLM_TIMEOUT_SECONDS=500`, `LLM_NATIVE_JSON_SCHEMA=true`, `DAALE_FORCE_IPV4=true`
- `LLM_EXPECTED_OUTPUT_TOKENS` defaults to 4000. The `OPENROUTER_*` lines remain but are ignored under `generic`.

Runtime state (gitignored): `data/yukti.db` (1 client, 1 key), `data/request_budget.<model>.json` (counts reset
by Pacific date), `secrets/portal.key`.

---

---

## 5. Files

**Created (R-Fabric):** `daale/intake.py`, `daale/providers.py`, `daale/budget.py`, `check_provider.py`,
`preflight.py`, `setup_env.ps1`, `.env.example`, `SERVICE.md`, `requirements-service.txt`,
`service/{__init__,app,store,security,manage_keys}.py`, tests `test_live_readiness.py`, `test_intake.py`,
`test_generic_client.py`, `test_budget.py`, `test_service.py`. `.gitignore` gained `data/` and `secrets/`.

**Modified (R-Fabric):** `daale/client.py`, `daale/pipeline.py` (rewritten orchestration),
`daale/execution_contract.py`, `daale/policy_engine.py`, `daale/prompts.py`, `run_daale.py`,
`tests/test_daale.py`.

**D-Core:** `rfabric.py` (reads unified findings), new `tests/test_rfabric_bridge_unified.py`.

**Added by the 2026-11-09 build:** `daale/replay.py`, `daale/network.py`, `live_check.py`, `set_key.py`; changes to
`client.py`, `providers.py`, `pipeline.py`, `policy_engine.py`, `execution_contract.py`, `prompts.py`,
`schemas.py`; D-Core `execution/commit.py`, `execution/dcore.py`, `rfabric.py`; ten new R-Fabric test files and
two D-Core ones; `docs/architecture/DECISION-005.md`, `DECISION-001.md`, `BRIEF-DECISION-005_2026-11-09.md`.

**This file:** `daale/imported/DAALE_2026-11-10/SESSION_LOG.md`.

---

## 6. How to run things

Set up (the repo's own `.venv` lacks `requests`, `jsonschema`, `python-dotenv`, FastAPI):

    cd daale/imported/DAALE_2026-11-10/R-Fabric
    pip install -r requirements.txt -r requirements-service.txt
    python preflight.py                      # readiness; prints no secrets
    python -m pytest tests -q                # 226 passed, 1 skipped (live test is opt-in)
    python check_provider.py --list          # one request: models on your key

Judgments:

    python run_daale.py --offline            # fixtures, no network
    python live_check.py                     # full live judgment + decision + replay (real requests)
    python live_check.py --base-only         # six kernels only
    python run_daale.py --live --resume runs/<trace>.json   # finish an incomplete run: only failed kernels + adversary
    python -m daale.replay runs/<trace>.json # recompute a decision from its recorded findings
    python set_key.py                        # hidden prompt; writes LLM_API_KEY to .env
    python run_daale.py --live               # sample case; 6 Gemma + 1 Gemini request
    python run_daale.py --live --material manifest.json
    python -m daale.budget status --model gemini-3.8-flash
    python -m daale.budget set 17 --model gemini-3.8-flash    # record usage made elsewhere

API:

    uvicorn "service.app:create_app_from_env" --factory --host 127.0.0.1 --port 8000
    python -m service.manage_keys create-client "Acme"
    python -m service.manage_keys issue-key cl_xxxx --label portal --out secrets/acme.key
    python -m service.manage_keys list | revoke key_xxxx | disable-client cl_xxxx

Log level: `DAALE_LOG_LEVEL` (default INFO), progress on stderr.

---

## 7. Open items

Resolved by the 2026-11-09 build: failed kernels forcing human review; kernel-disagreement policy (unanimity);
DECISION-005; the bridge's WEAKENS labelling; unassessed requirements missing from the summary; the
`degradation_mode` naming; CONTRARIAN and OUTSIDER failures; the slow connections.

**Do first**
1. **Rotate the exposed keys:** the keys displayed in earlier chats, the Google key pasted in chat (it is in
   that conversation's history and a local transcript), three OpenRouter keys in plaintext on `D:`, and the
   contents of `choir/openrouter api.txt` (untracked and not gitignored). The zip in Downloads contains a live `.env`.
2. **Commit.** Nothing is committed and the real repository has none of these changes. When carrying them
   over, the main `.env` needs the four settings in section 4.

**Engine**
3. Run `python live_check.py` on any server that will host the engine; it detects a broken IPv6 route.
4. How a human review is recorded and closed: a `REVIEW_REQUIRED` candidate is not stored anywhere durable.
5. DECISION-007 should record the extra `REVIEW_REQUIRED` escalation reason (that ADR is not in the baseline).
6. `content_hash` is never verified against text, and the sample case's hashes are placeholders: decide what
   the hash covers.
7. `--resume` is built, tested offline and verified live (section 3.13). Not yet exercised live: resuming when only
   the adversary failed, and a resume whose budget is too small.
7a. (Resolved 2026-11-11, section 3.17: a complete live ADVANCE on Gemini.) Earlier note: **No complete live ADVANCE yet.** DD-003 reached the policy's ADVANCE on every substantive point but was blocked
   by a failed HISTORIAN (output truncated at 16,000 tokens). Resume it, and consider a one-time retry of a truncated
   kernel with a short "answer directly" nudge, since this is the second kernel to loop in its reasoning.
   (Both are now built, section 3.15; not yet exercised live.)

**Quota and cost**
8. Gemini allows 20 requests a day (about 3 judgments with retries). Options: a lean kernel profile (changes
   independence, needs sign-off), a different adversary model, or a paid tier.
9. Free-tier reliability: 16 of Gemma's answers in one run were 503 or 500. Decide on a paid tier or a second
   provider before a five-user portal.
10. Gemma's 16K tokens per minute caps case size at roughly 30,000 characters per request.
11. Check Google's free-tier data-use terms before any real client material goes through it.

**Product**
12. Pick one API: the report mentions an earlier `daale_api` (Oct 26; D-Core admission, shared keys) and the
    `service/` here (per-client keys). They have not been compared.
13. Policies must be authored per decision type; intake does not create them.
14. Deployment (server, HTTPS, DNS, backups, budget alerts), the client portal with its user login and a
    server-side key forwarder: none exist.
15. Not built in `service/`: key rotation, idempotency keys, per-client quotas, D-Core admission of API results,
    a hosted database.

**Facts to remember**
- A live judgment is 7 requests and, per the report, about 16 minutes at current caps.
- The adversary seeing a different model family than the kernels is deliberate.
- Only the synthetic sample case has run live. A pass shows schema-valid, reproducible findings that D-Core
  accepts; it does not show the judgment is correct. Nothing has run against real client data.
