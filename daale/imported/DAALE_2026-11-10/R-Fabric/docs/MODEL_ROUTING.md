# Ordered model routing

DAALE uses only model IDs explicitly supplied in its environment. There is no
model catalog lookup, automatic provider change, or implicit paid-model route.

Configure one primary with up to three ordered fallback IDs:

```dotenv
DAALE_DEFAULT_MODEL=model-a
DAALE_FALLBACK_MODEL=model-b,model-c,model-d
```

`DAALE_<KERNEL>_MODEL` selects a kernel-specific primary. Its
`DAALE_<KERNEL>_FALLBACK_MODEL` replaces the default fallback list for that
kernel. Each resolved chain can contain at most four distinct, non-empty IDs.
Add each selected model to `LLM_LIMITS` when provider request or token limits
need local pacing.

For a run, kernels walk their configured chain in order. A model unavailable
for the configured provider is marked `DEAD` for the run. A provider
authentication failure marks that provider `DEAD`, because another model on
the same credential will not repair the key. Per-minute rate limits and daily
quota place a model in `COOLING`; it becomes eligible when the recorded
Retry-After or budget reset expires. Temporary outages, timeouts, truncation,
and invalid output do not mark a model unhealthy. They follow the existing
retry and fallback rules.

Base kernels run concurrently. A request already in flight when another
kernel marks a model `DEAD` or `COOLING` cannot be recalled; later kernels
skip it and record `kernel-model-skipped`. The adversary runs after the base
kernels and sees the run's current health map.

Traces preserve the configured chain, provider, requested and served model,
HTTP attempt count, usage, output ceiling, failure events, fallback events,
and the model-health snapshot. Replay continues to use the recorded findings
and policy; it does not call a model or re-select a route.

## Operator boundaries

- Keep the fallback list explicit and within the approved budget.
- A model change may change analytical output; it does not change policy or
  decision authority. Compare route provenance when reviewing judgments.
- Cooling is per pipeline run. A new run starts with fresh health state and
  uses the configured preferred model again.
