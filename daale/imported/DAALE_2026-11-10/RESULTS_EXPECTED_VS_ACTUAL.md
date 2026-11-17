# Expected versus actual: every live run we have a trace for

Generated from the saved traces; nothing was sent to any provider to build it. Offline fixture runs are left out (they replay canned answers, not a model). Times are UTC.

## Per case: the expectation and the best result

| Case | Expected | How the expectation was set | Live runs | Best outcome |
|---|---|---|---|---|
| DD-001 | REJECT | design: the sample case is built so two critical requirements fail (no SOC 2, incomplete questionnaire) | 18 | MATCH |
| DD-002 | ADVANCE | registered before the run | 2 | MISS (substance) |
| DD-003 | ADVANCE | registered before the run (after seeing DD-002) | 2 | MATCH |
| INV-BANK-A | ADVANCE | registered before the run (test later abandoned) | 1 | MISS (infrastructure) |
| INV-BANK-B | REJECT | registered before the run (test later abandoned) | 1 | MISS (infrastructure) |

Cases that were set up but never produced a trace: INV-LOGISTICS-A (expected ADVANCE) and INV-LOGISTICS-B (expected REJECT). Both were refused before any request because the daily Gemini budget counter had reached 0.

## Every live run, oldest first

| Run (UTC) | Case | Expected | Final decision | Rule | Policy state before the integrity rule | Failed kernels | Adversary | Models | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 2026-08-29 14:43 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | FIRST_PRINCIPLES, OUTSIDER, CONTRARIAN, EXPANSIONIST, ANALYST, HISTORIAN | ? | none | **NO ANSWER** |
| 2026-08-29 14:49 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | EXPANSIONIST, CONTRARIAN, ANALYST, FIRST_PRINCIPLES, HISTORIAN, OUTSIDER | ? | none | **NO ANSWER** |
| 2026-09-10 17:14 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | ANALYST, CONTRARIAN, HISTORIAN, FIRST_PRINCIPLES, OUTSIDER, EXPANSIONIST | ? | none | **NO ANSWER** |
| 2026-09-17 14:09 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | OUTSIDER, HISTORIAN, FIRST_PRINCIPLES, CONTRARIAN, EXPANSIONIST, ANALYST | ? | none | **NO ANSWER** |
| 2026-09-17 14:41 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | FIRST_PRINCIPLES, EXPANSIONIST, CONTRARIAN, OUTSIDER, ANALYST, HISTORIAN | ? | none | **NO ANSWER** |
| 2026-09-17 15:52 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | CONTRARIAN, HISTORIAN, ANALYST, OUTSIDER, EXPANSIONIST, FIRST_PRINCIPLES | ? | none | **NO ANSWER** |
| 2026-09-17 16:02 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | HISTORIAN, EXPANSIONIST, ANALYST, OUTSIDER, CONTRARIAN, FIRST_PRINCIPLES | ? | none | **NO ANSWER** |
| 2026-09-17 16:05 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | OUTSIDER, ANALYST, FIRST_PRINCIPLES, EXPANSIONIST, CONTRARIAN, HISTORIAN | ? | none | **NO ANSWER** |
| 2026-09-17 19:49 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | FIRST_PRINCIPLES, ANALYST, HISTORIAN, CONTRARIAN, OUTSIDER, EXPANSIONIST | ? | none | **NO ANSWER** |
| 2026-09-17 20:03 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | HISTORIAN, FIRST_PRINCIPLES, ANALYST, EXPANSIONIST, CONTRARIAN, OUTSIDER | ? | none | **NO ANSWER** |
| 2026-09-17 20:04 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | HISTORIAN, OUTSIDER, CONTRARIAN, FIRST_PRINCIPLES, EXPANSIONIST, ANALYST | ? | none | **NO ANSWER** |
| 2026-09-17 20:08 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | OUTSIDER, EXPANSIONIST, ANALYST, HISTORIAN, CONTRARIAN, FIRST_PRINCIPLES | ? | none | **NO ANSWER** |
| 2026-09-17 20:11 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | FIRST_PRINCIPLES, HISTORIAN, OUTSIDER, ANALYST, EXPANSIONIST, CONTRARIAN | ? | none | **NO ANSWER** |
| 2026-11-08 10:34 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | none | failed | gemini-3.8-flash | **MISS (infrastructure)** |
| 2026-11-08 11:15 | DD-001 | REJECT | REJECT | `P080-CRITICAL-FAILURE` | - | CONTRARIAN, OUTSIDER | ran | gemini-3.8-flash, gemma-4-31b-it | **MATCH** |
| 2026-11-09 10:09 | DD-001 | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | none | failed | gemma-4-31b-it | **MISS (infrastructure)** |
| 2026-11-09 10:35 | DD-001 | REJECT | REJECT | `P080-CRITICAL-FAILURE` | - | none | ran | gemini-3.8-flash, gemma-4-31b-it | **MATCH** |
| 2026-11-10 09:12 | DD-001 | REJECT | REJECT | `P080-CRITICAL-FAILURE` | - | none | ran | gemini-3.8-flash, gemma-4-31b-it | **MATCH** |
| 2026-11-10 10:11 | DD-002 | ADVANCE | ESCALATE | `DEGRADED-EXECUTION` | - | OUTSIDER | failed | gemma-4-31b-it | **INCONCLUSIVE** |
| 2026-11-10 10:55 | DD-002 (resume) | ADVANCE | ESCALATE | `P100-HIGH-CHALLENGE` | - | none | ran | gemini-3.8-flash, gemma-4-31b-it | **MISS (substance)** |
| 2026-11-10 11:33 | DD-003 | ADVANCE | ESCALATE | `INCOMPLETE-RUN-ADVANCE-BLOCKED` | ADVANCE | HISTORIAN | ran | gemini-3.8-flash, gemma-4-31b-it | **MISS (infrastructure)** |
| 2026-11-10 12:14 | INV-BANK-A | ADVANCE | ESCALATE | `INCOMPLETE-RUN-ADVANCE-BLOCKED` | ADVANCE | FIRST_PRINCIPLES, EXPANSIONIST | ran | gemini-3.8-flash, gemma-4-31b-it | **MISS (infrastructure)** |
| 2026-11-10 12:41 | INV-BANK-B | REJECT | ESCALATE | `DEGRADED-EXECUTION` | - | EXPANSIONIST | failed | gemma-4-31b-it | **MISS (infrastructure)** |
| 2026-11-11 11:09 | DD-003 | ADVANCE | ADVANCE | `P050-ALL-MANDATORY-SATISFIED` | - | none | ran | gemini-3.8-flash | **MATCH** |

## Notes per run

- **2026-08-29 14:43 DD-001** (DD-001-20260829T144311413251Z-6f9f8afdbf8c.json): no model call produced an answer (failed before any kernel finished). Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: no requirement verdicts. Decision recomputed from the findings: HOLD.
- **2026-08-29 14:49 DD-001** (DD-001-20260829T144936949602Z-57c915792b8f.json): no model call produced an answer (failed before any kernel finished). Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: no requirement verdicts. Decision recomputed from the findings: HOLD.
- **2026-09-10 17:14 DD-001** (DD-001-20260910T171412092084Z-17e0416b496b.json): no model call produced an answer (failed before any kernel finished). Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: no requirement verdicts. Decision recomputed from the findings: HOLD.
- **2026-09-17 14:09 DD-001** (DD-001-20260917T140957500213Z-c9db30c0ca14.json): no model call produced an answer (failed before any kernel finished). Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: no requirement verdicts. Decision recomputed from the findings: HOLD.
- **2026-09-17 14:41 DD-001** (DD-001-20260917T144116492534Z-c8736b6c4fad.json): no model call produced an answer (failed before any kernel finished). Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: no requirement verdicts. Decision recomputed from the findings: HOLD.
- **2026-09-17 15:52 DD-001** (DD-001-20260917T155256726326Z-95e8ad5a1f4b.json): no model call produced an answer (failed before any kernel finished). Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: no requirement verdicts. Decision recomputed from the findings: HOLD.
- **2026-09-17 16:02 DD-001** (DD-001-20260917T160227325688Z-f546c75dd914.json): no model call produced an answer (failed before any kernel finished). Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: no requirement verdicts. Decision recomputed from the findings: HOLD.
- **2026-09-17 16:05 DD-001** (DD-001-20260917T160502445670Z-dda2d52bb222.json): no model call produced an answer (failed before any kernel finished). Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: no requirement verdicts. Decision recomputed from the findings: HOLD.
- **2026-09-17 19:49 DD-001** (DD-001-20260917T194916625660Z-8ace048fbc0c.json): no model call produced an answer (failed before any kernel finished). Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: no requirement verdicts. Decision recomputed from the findings: HOLD.
- **2026-09-17 20:03 DD-001** (DD-001-20260917T200302716679Z-27f7eeea695a.json): no model call produced an answer (failed before any kernel finished). Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: no requirement verdicts. Decision recomputed from the findings: HOLD.
- **2026-09-17 20:04 DD-001** (DD-001-20260917T200430508700Z-7e9af7e4f0a2.json): no model call produced an answer (failed before any kernel finished). Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: no requirement verdicts. Decision recomputed from the findings: HOLD.
- **2026-09-17 20:08 DD-001** (DD-001-20260917T200810079536Z-acbfa4d3aebb.json): no model call produced an answer (failed before any kernel finished). Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: no requirement verdicts. Decision recomputed from the findings: HOLD.
- **2026-09-17 20:11 DD-001** (DD-001-20260917T201139472269Z-af44085ba63f.json): no model call produced an answer (failed before any kernel finished). Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: no requirement verdicts. Decision recomputed from the findings: HOLD.
- **2026-11-08 10:34 DD-001** (DD-001-20261108T103401942541Z-378d31914f01.json): the run was incomplete; the findings available point to REJECT. Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: R1 NOT_SATISFIED, R2 NOT_SATISFIED, R3 UNKNOWN, R4 UNKNOWN. Decision recomputed from the findings: REJECT.
- **2026-11-08 11:15 DD-001** (DD-001-20261108T111525218244Z-131e87325c5b.json): final decision equals the expectation. Requirements in the packet: {'R1': 'NOT_SATISFIED', 'R2': 'NOT_SATISFIED', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: R1 NOT_SATISFIED, R2 NOT_SATISFIED, R3 UNKNOWN, R4 UNKNOWN. Decision recomputed from the findings: REJECT.
- **2026-11-09 10:09 DD-001** (DD-001-20261109T100949488817Z-94ce83513ded.json): the run was incomplete; the findings available point to REJECT. Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: R1 NOT_SATISFIED, R2 NOT_SATISFIED, R3 UNKNOWN, R4 UNKNOWN. Decision recomputed from the findings: REJECT.
- **2026-11-09 10:35 DD-001** (DD-001-20261109T103535370146Z-1d2b2028c5dd.json): final decision equals the expectation. Requirements in the packet: {'R1': 'NOT_SATISFIED', 'R2': 'NOT_SATISFIED', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: R1 NOT_SATISFIED, R2 NOT_SATISFIED, R3 UNKNOWN, R4 UNKNOWN. Decision recomputed from the findings: REJECT.
- **2026-11-10 09:12 DD-001** (DD-001-20261110T091238982750Z-c991e89934f5.json): final decision equals the expectation. Requirements in the packet: {'R1': 'NOT_SATISFIED', 'R2': 'NOT_SATISFIED', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: R1 NOT_SATISFIED, R2 NOT_SATISFIED, R3 UNKNOWN, R4 UNKNOWN. Decision recomputed from the findings: REJECT.
- **2026-11-10 10:11 DD-002** (DD-002-20261110T101123189551Z-1bd5ca46e042.json): the run was incomplete and the findings available do not settle it. Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: R1 SATISFIED, R2 SATISFIED, R3 SATISFIED, R4 SATISFIED. Decision recomputed from the findings: ESCALATE.
- **2026-11-10 10:55 DD-002** (DD-002-20261110T105520456421Z-21166dcc2166.json): a complete run reached a different decision than expected. Requirements in the packet: {'R1': 'SATISFIED', 'R2': 'SATISFIED', 'R3': 'SATISFIED', 'R4': 'SATISFIED'}. Verdicts from the kernels themselves: R1 SATISFIED, R2 SATISFIED, R3 SATISFIED, R4 SATISFIED. Decision recomputed from the findings: ESCALATE.
- **2026-11-10 11:33 DD-003** (DD-003-20261110T113332542115Z-f758761d7be3.json): the run was incomplete; the findings available point to ADVANCE. Requirements in the packet: {'R1': 'SATISFIED', 'R2': 'SATISFIED', 'R3': 'SATISFIED', 'R4': 'SATISFIED'}. Verdicts from the kernels themselves: R1 SATISFIED, R2 SATISFIED, R3 SATISFIED, R4 SATISFIED. Decision recomputed from the findings: ESCALATE.
- **2026-11-10 12:14 INV-BANK-A** (INV-BANK-A-20261110T121444923982Z-09bfda6b1d28.json): the run was incomplete; the findings available point to ADVANCE. Requirements in the packet: {'R1': 'SATISFIED', 'R2': 'SATISFIED', 'R3': 'SATISFIED', 'R4': 'SATISFIED'}. Verdicts from the kernels themselves: R1 SATISFIED, R2 SATISFIED, R3 SATISFIED, R4 SATISFIED. Decision recomputed from the findings: ESCALATE.
- **2026-11-10 12:41 INV-BANK-B** (INV-BANK-B-20261110T124116759261Z-07d299387e26.json): the run was incomplete; the findings available point to REJECT. Requirements in the packet: {'R1': 'UNKNOWN', 'R2': 'UNKNOWN', 'R3': 'UNKNOWN', 'R4': 'UNKNOWN'}. Verdicts from the kernels themselves: R1 SATISFIED/UNKNOWN, R2 NOT_SATISFIED, R3 NOT_SATISFIED, R4 SATISFIED. Decision recomputed from the findings: REJECT.
- **2026-11-11 11:09 DD-003** (DD-003-20261111T110927629219Z-54694df58271.json): final decision equals the expectation. Requirements in the packet: {'R1': 'SATISFIED', 'R2': 'SATISFIED', 'R3': 'SATISFIED', 'R4': 'SATISFIED'}. Verdicts from the kernels themselves: R1 SATISFIED, R2 SATISFIED, R3 SATISFIED, R4 SATISFIED. Decision recomputed from the findings: ADVANCE.

## How to read the verdicts

- **MATCH**: the final decision equals the expectation.
- **MISS (infrastructure)**: the final decision differs, but the run was incomplete (a kernel or the adversary failed, or an incomplete run was blocked from ADVANCE) and the findings that did arrive point to the expected decision.
- **INCONCLUSIVE**: incomplete, and the available findings do not settle the question.
- **MISS (substance)**: a complete run reached a different decision. None of the rows above are in this class unless marked.
- **NO ANSWER**: failed before any kernel produced a finding.
- DD-001's expectation comes from how the sample case was built, not from a file registered before running; the others were registered first.
- DD-002 is a case where my expectation was wrong in a way the engine could defend (claim C2 had no direct evidence), so its MISS is not evidence against the engine.
- Gemma 4 on the free tier, not the engine's logic, accounts for most of the infrastructure misses.
