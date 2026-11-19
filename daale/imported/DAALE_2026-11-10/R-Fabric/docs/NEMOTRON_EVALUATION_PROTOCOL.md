# Nemotron evaluation protocol

## Boundary

Nemotron is not integrated into the live DAALE pipeline by this phase. The
provider-neutral interface in `daale/evaluation_adapter.py` is a contract for
a future evaluation-only adapter. The adapter handles one explicitly named
model per request; it does not select fallback models, combine kernel
opinions, synthesize judgments, or change policy authority.

Each request must specify the provider and exact requested model, kernel
purpose, messages, JSON schema, reasoning-effort setting, output-token ceiling,
and timeout. Each response or failure must preserve provider/model identity,
attempt count, request ID, usage, output ceiling, structured-output mode,
and classified failure details. A response must identify both requested and
served model. Missing provider token usage remains `null`; it must not be
invented. The caller validates the structured output against the same kernel
schema used for Gemini.

## Registered blind set

At protocol start, enumerate every `cases/expected/*.expected.json` and
validate that its referenced case and policy exist. The currently registered
set includes:

- `vendor_beta`, `vendor_gamma`
- `inv_bank_a`, `inv_bank_b2`, `inv_logistics_a`, `inv_logistics_b`,
  `inv_stress_1`

Record SHA-256 digests of each case, policy, and expected file in the
evaluation manifest. Never modify those files to improve a score. The runner
and model adapter receive only the case and policy; expected files remain in
the scoring step and are not included in prompts, adapter requests, or
operator-supplied model instructions.

## Paired evaluation sequence

1. Pin the repository commit, Python environment, prompt-separation flag,
   policy version, provider settings, and exact Gemini and Nemotron model IDs.
   Disable fallback and dynamic route switching for the comparison so each
   result can be attributed to the requested model. Set a request/token or
   spend ceiling approved before the run; do not infer free access from a
   model name.
2. For a case, capture a complete Gemini baseline trace using the current
   canonical kernel mapping. Record the trace hash and keep it immutable.
3. Repeat the same case and policy with exactly one kernel assigned to
   Nemotron; keep all other kernel models and settings identical. This paired
   single-kernel replacement isolates the changed role. Run the adversary as
   its own replacement only after its input base outputs are fixed and
   recorded. Use fresh run IDs and retain every partial or failed trace.
4. Begin with `inv_stress_1`, prioritizing HISTORIAN (injection exposure),
   ANALYST (volume), and the two kernels with prior truncation history. Then
   extend to the remaining registered cases only when the first stage is
   within the pre-approved budget. A smaller case may be used first solely as
   an adapter connectivity check; it is not a quality result.
5. Validate every output against the existing schema and evidence IDs before
   synthesis. Replay the deterministic policy from the recorded findings.
   Only after traces are sealed, score the result against the registered
   expectation and review the rationales and citations.

## Report each pair

For each case/kernel pair, report:

- complete, partial, or failed execution and the exact failure class;
- requested/served model, provider, attempts, ceilings, usage, and request IDs;
- schema validity, required relation coverage, invalid references, and
  evidence-citation integrity;
- kernel verdicts and disagreements, adversarial challenges, deterministic
  policy state/rule, and replay result;
- registered expected tier and post-run score, clearly separated from
  execution integrity;
- differences attributable to the replaced kernel, without implying that a
  single pair establishes general model superiority.

Do not accept one favorable policy outcome as proof of quality. A model that
returns the expected state with invalid evidence use, omitted required
relations, or an incomplete run is not a successful evaluation. Any move from
evaluation adapter to production provider requires a separate review of
provider terms, data handling, rate limits, cost, and approval of the exact
model and reasoning-effort settings.
