# Session report, 2026-11-09 (YUKTI / DAALE engine)

Working copy: `D:\DAALE_2026-11-08\DAALE`. It is a snapshot, not a git repository, so **nothing here is committed or deployed**. Your real repository has none of these changes yet.

## 1. Result in one screen

| Question | Answer |
|----------|--------|
| Do all six kernels run on the real model? | **Yes, 6 of 6.** `python live_check.py` passed at 16:05 (exit 0, 15 min 57 s). Six kernels on Gemma 4 31B, then the adversary. |
| Does the adversary run? | Yes: `gemini-3.8-flash`, on its first try, in 285 s. |
| What did it decide on the sample case? | **REJECT**, rule `P080-CRITICAL-FAILURE`. R1 and R2 are `NOT_SATISFIED` (evidence E3), R3 and R4 are `UNKNOWN`, claim C1 is `CONTRADICTED` and C2 `INSUFFICIENT_EVIDENCE`. Human review not required. |
| Does the decision replay? | Yes. `python -m daale.replay` recomputed REJECT identically from the recorded findings (8 fields compared). |
| Does D-Core accept it? | Yes: committed. Every active gate check passed (the execution-plan check is inactive until Phase 3). |
| Offline tests | R-Fabric: 167 passed, 1 skipped (the opt-in live test); its service tests are excluded because FastAPI is not installed. D-Core: 107 passed. |
| Committed or deployed | No. |

Trace of the passing run: `DAALE\R-Fabric\runs\DD-001-20261109T103535370146Z-1d2b2028c5dd.json`.

## 2. Why it was slow, and why the first full run failed

**The slowness was your network, not Google's queue.** Earlier today I told you Google queues every free-tier request for about three minutes. That was wrong, and the notes that said so are corrected. Google's address list starts with eight IPv6 addresses. IPv6 does not work on your connection, so each address hangs about 21 s before the PC tries the next, and every new connection lost 8 x 21 = 169 s before it fell back to IPv4. Measured: listing the models took 169.2 s, a request Google rejects at once took 169.1 s, and with IPv4 forced both took about 1.2 s. That one cause produced the "190 s to first token", the 400 errors that came back after 170 s, and read timeouts that fired at 669 s instead of 500 s.

**The first full run (14:38 to 15:39) failed only at the last step.** All six kernels passed, then the Gemini adversary failed all three attempts: each ended in a 500 s read timeout, and two of them began with a 503 "high demand". Each attempt also paid the 169 s. DAALE does not judge without its adversary, so it escalated to a human as `DEGRADED-EXECUTION`, which is the design working.

**The fix** is `DAALE_FORCE_IPV4=true` (now in your `.env`), `daale/network.py`, and `live_check.py`, which detects the problem and switches itself with a message. With it the same check ran in 16 minutes and passed.

**What is still slow:** Google's Gemma servers answered with HTTP 503 "high demand" or 500 sixteen times in the passing run (11 x 503, 5 x 500). Four of the six kernels failed their first attempt and passed on the second. That is the free tier's capacity, and the retries absorbed it.

## 3. What you asked, and what happened

| # | You asked | Outcome |
|---|-----------|---------|
| 1 | Remember the old DAALE context and merge the new `SESSION_LOG.md` | Done. 16 memory notes now (names, architecture, timeline, decisions, quotas, constraints, file locations, the IPv6 finding). |
| 2 | Token ceiling 16000 | Done in the snapshot (code defaults in `providers.py` and `client.py`, and `.env.example`). Your main-repo `.env` was not on `D:`, so it still needs `LLM_MAX_TOKENS=16000`. |
| 3 | Use my Google AI Studio key, add pacing, every model may take up to 500 s | The key was never written, read or printed by me; you saved it in `.env` yourself, and `set_key.py` (hidden prompt) exists for next time. Timeout is 500 s for every model (connecting fails after 30 s). Retries wait as long as Google asks (`Retry-After` or `retryDelay`, 1 to 65 s). Per-model request and token pacing was already there. |
| 4 | Fix the Contrarian output length and the Outsider schema failure | Both fixed, with different causes (section 4). |
| 5 | Resolve the requirement-assessment and bridge inconsistencies | Done: unanimity rule, bridge relations, unassessed requirements, `degradation_mode: none`. |
| 6 | Decide whether a failed kernel must force human review | Decided yes. An incomplete run can never `ADVANCE`. |
| 7 | Resolve DECISION-005 explicitly | You chose option 1 (R-Fabric evaluates, D-Core commits). Ratified with four conditions, all implemented. |
| 8 | "Use this model" | Kept: six kernels on `gemma-4-31b-it`, adversary on `gemini-3.8-flash`, Google's OpenAI-compatible endpoint. |
| 9 | "Isn't this just an agent with multiple prompts?" | Answered in chat. |
| 10 | Show me a live judgement | At that point there was no complete live result from this session, and I said so. There is one now (section 1). |
| 11 | Make a test for 6 of 6; repair and rerun if it fails | `live_check.py` is that test. It failed once at the adversary, I found the network cause, repaired it, and it passed on the rerun. |
| 12 | Why is it taking time, why did it fail, and a report | Section 2 and this document. |

## 4. What was actually wrong, and the fix

1. **IPv6 failover cost 169 s per connection** (section 2). Fix: `DAALE_FORCE_IPV4=true`.
2. **CONTRARIAN never failed because of the length limit.** Streaming the call showed Gemma 4 spending the whole 16,000-token budget on hidden reasoning (about 44,600 characters of `<thought>`, a loop re-listing the same requirements) and returning no answer. That also explains the Nov-8 cut-offs at 8,000 tokens. Raising the ceiling could never fix it. Fix: strict structured output (`LLM_NATIVE_JSON_SCHEMA=true`). The same call then returned a valid 14-finding answer in 1,749 tokens. Your main-repo `.env` needs this line too.
3. **OUTSIDER failed twice with the same error because the retry was blind.** The schema check lives in the client, which raised an error that carried no copy of the rejected reply, so the pipeline never told the model what was wrong. Fixes: the rejected reply is attached to the error, the repair message names each finding and the one-line fix, and the prompts say to use `GENERAL` for a whole-case finding.
4. **One stalled call cost 3 x 500 s.** A read timeout was retried at the HTTP layer and again at the kernel layer. The HTTP layer no longer retries a read timeout.
5. **"Last kernel wins" for requirement verdicts.** Replaced by `aggregate_requirement_assessments`: a requirement is `SATISFIED` or `NOT_SATISFIED` only if every kernel that assessed it agrees, otherwise `UNKNOWN`. A requirement nobody assessed is `UNKNOWN` and listed.
6. **The D-Core bridge labelled every unsatisfied requirement `WEAKENS`.** Now `SATISFIED` maps to `SUPPORTS`, `NOT_SATISFIED` to `CONTRADICTS`, `UNKNOWN` to `CONTEXTUAL`.
7. **A clean run reported degradation mode `retry`.** Now `none`.

## 5. Decisions recorded

- **DECISION-005 (Approved 2026-11-09), option 1: R-Fabric evaluates, D-Core commits.** Conditions: (1) DECISION-001 narrowed: model kernels produce advisory, replayable findings, and only deterministic code decides; (2) `python -m daale.replay <trace>` recomputes a decision from its recorded findings; (3) a packet flagged `requires_human_review` goes to `REVIEW_REQUIRED` in the D-Core gate instead of being committed; (4) the authority notice stays.
- **Any failed kernel forces human review.** An incomplete run never emits `ADVANCE`; it becomes `ESCALATE` under `INCOMPLETE-RUN-ADVANCE-BLOCKED`, and the policy's own result stays visible in the packet. A contested mandatory or critical requirement also forces review.
- **Kernel disagreement is resolved by unanimity, otherwise `UNKNOWN`.**

## 6. Files changed (all inside the snapshot)

**R-Fabric engine** (`DAALE/R-Fabric/daale/`): `client.py`, `providers.py`, `pipeline.py`, `policy_engine.py`, `execution_contract.py`, `prompts.py`, `schemas.py`, and new `replay.py` and `network.py`.
**R-Fabric scripts and docs:** new `live_check.py` and `set_key.py`; `.env.example` and `README.md` (sections on combining verdicts, incomplete runs, replay, live check, IPv4).
**R-Fabric tests (new):** `test_set_key`, `test_prompts`, `test_timeouts_and_retry`, `test_requirement_aggregation`, `test_integrity_rules`, `test_replay`, `test_repair`, `test_live_check`, `test_live_six_kernels` (live, only with `DAALE_LIVE=1`), `test_network`.
**D-Core:** `rfabric.py`, `execution/commit.py` (`Candidate.needs_review`), `execution/dcore.py`, `README.md`; new tests `test_review_flag` and `test_rfabric_bridge_requirements`; `test_conformance` and `test_execution` changed on purpose, because they had pinned DECISION-005 as open.
**Docs:** `docs/architecture/DECISION-005.md` (full ADR), `DECISION-001.md` (amendment), `BRIEF-DECISION-005_2026-11-09.md` (options considered), root `README.md` (link fix).
**Your `.env`:** I never read it. Scripts added only non-secret lines (models, limits, `LLM_MAX_TOKENS`, `LLM_TIMEOUT_SECONDS`, `LLM_NATIVE_JSON_SCHEMA`, `DAALE_FORCE_IPV4`).

## 7. Live evidence

Passing run, `python live_check.py`, started 15:49:38 on the synthetic case `vendor_alpha` with the vendor post-technical-DD policy (base kernels done 16:00:50, adversary done 16:05:35):

| Kernel | Result | Attempts | Time of the winning attempt | Tokens |
|--------|--------|----------|-----------------------------|--------|
| FIRST_PRINCIPLES | ok | 1 | 115 s | 4,128 |
| OUTSIDER | ok | 1 | 316 s | 4,302 |
| CONTRARIAN | ok | 2 | 96 s | 4,577 |
| EXPANSIONIST | ok | 2 | 81 s | 4,366 |
| HISTORIAN | ok | 2 | 92 s | 4,287 |
| ANALYST | ok | 2 | 375 s | 4,184 |
| ADVERSARY (Gemini) | ok | 1 | 285 s | 20,091 |

Findings per kernel: 12, 14, 12, 14, 15, 13 for the six, 3 for the adversary. Served models: `gemma-4-31b-it` six times, `gemini-3.8-flash` once. The passing attempts were short; most of the wall time was the 16K tokens/min pacing and the failed first attempts.

**Reproducibility:** all six kernels returned byte-identical outputs in the two full runs an hour apart (same prompts, temperature 0, strict schema). That supports replay as an audit method, though it is not guaranteed in general.

**Requests used today (Pacific day):** Gemini 6 of 20, Gemma 53 of 14,400.

**Measured earlier today on Gemma 4 31B** (the first-token delay numbers from that session are discarded, see section 2): about 30 tokens/s once generating, about 116 hidden reasoning tokens even for a 5-token reply, no way to switch thinking off (a `reasoning_effort` or thinking field returns HTTP 400), strict JSON-schema output accepted with no hidden reasoning.

## 8. Still open: yours to do or decide

1. **Rotate keys.** The Google key you pasted in chat sits in this conversation's history and in a local transcript file. Also outstanding: three OpenRouter keys in plaintext on `D:`, two keys leaked in earlier chats, and `choir/openrouter api.txt`.
2. **Carry the changes into your real repository and commit.** The list is in section 6 and in the memory note `daale-changes-2026-11-09`. Add to the main `.env`: `LLM_MAX_TOKENS=16000`, `LLM_TIMEOUT_SECONDS=500`, `LLM_NATIVE_JSON_SCHEMA=true`, `DAALE_FORCE_IPV4=true`.
3. **Run `python live_check.py` on any server that will host the engine.** It detects a broken IPv6 route and says so.
4. **Pick one API:** `daale_api` (Oct 26; D-Core admission, shared keys) or `service/` (Nov 8; per-client keys).
5. **DECISION-007** should record the extra `REVIEW_REQUIRED` escalation reason; that ADR is not in the snapshot.
6. **`content_hash`** is never verified and the sample case's hashes are visibly made up; it needs a decision on what the hash covers.
7. **How a human review is recorded and closed** is not decided: a `REVIEW_REQUIRED` candidate is not stored anywhere durable.
8. **Check Google's free-tier data-use terms** before any real client material goes through it.
9. **Free-tier reliability before a five-user portal:** 16 of Gemma's answers in one run were 503 or 500, and Gemini allows 20 requests a day. A paid tier or a second provider is a decision for you.
10. Unchanged from the handoff list: policies per decision type, deployment (server, HTTPS, DNS, backups), the client portal, per-client quotas and idempotency in `service/`.
11. Not built: resuming only the adversary from a saved trace. A refused run keeps the six base results in its trace, so the 11 minutes of kernel work are not lost, but there is no command to reuse them.

## 9. How to rerun

```powershell
cd D:\DAALE_2026-11-08\DAALE\R-Fabric
python live_check.py              # full judgment: six kernels, adversary, decision, replay
python live_check.py --base-only  # six kernels only
python -m daale.replay runs\<trace>.json
```

Exit status of `live_check.py`: 0 pass, 1 a kernel or the adversary failed, 2 could not start (no key, budget used).

## Limits of what this shows

- A pass means every kernel returned schema-valid findings, the decision is reproducible from them, and D-Core accepts the packet. It does **not** show the judgment is correct. Only the synthetic sample case was run, and it is built so that two critical requirements fail; REJECT agrees with your Nov-8 live result and with the offline fixtures, which shows consistency on an easy case, not accuracy on hard ones.
- The September "15x / 7-of-7" results came from hand-authored fixtures and are not live evidence.
- Nothing was run against real client material.
