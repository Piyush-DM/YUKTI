# YUKTI engine API

The portal talks only to this service. The model provider key stays in the
server's `.env`; each client organisation gets its own key.

## Run

    pip install -r requirements.txt -r requirements-service.txt
    uvicorn "service.app:create_app_from_env" --factory --host 127.0.0.1 --port 8000

The service speaks plain HTTP. Put HTTPS in front of it (Caddy or nginx) before
exposing it, and set `YUKTI_CORS_ORIGINS` to the portal's origin.

## Clients and keys (server-side only, no HTTP admin)

    python -m service.manage_keys create-client "Acme Capital"
    python -m service.manage_keys issue-key cl_xxxx --label portal --out secrets/acme.key
    python -m service.manage_keys list
    python -m service.manage_keys revoke key_xxxx
    python -m service.manage_keys disable-client cl_xxxx

A key is shown once and only its SHA-256 is stored. Send it as
`Authorization: Bearer <key>`. Never put it in browser JavaScript: the portal's
own backend (or a serverless function) should hold it and call the API.

## Endpoints (all under /v1; all but health need the key)

| Method | Path | Purpose |
|---|---|---|
| GET | /health | status, provider, model, policy ids (no auth) |
| POST | /judgments | start a judgment; returns 202 and a `judgment_id` |
| GET | /judgments | your judgments, newest first |
| GET | /judgments/{id} | status, and the decision when complete |
| GET | /judgments/{id}/audit | the full record: case, prompts, calls, findings |
| GET | /cases, /cases/{case_id} | judgments grouped by `case_id` |
| GET | /usage | judgments, model calls, tokens |

### Start a judgment

    {"policy_id": "VENDOR-POST-TECH-DD",
     "material": {
       "case_id": "DD-2026-014",
       "decision_stage": "post_technical_due_diligence_approval",
       "decision_question": "Approve the vendor?",
       "claims": [{"claim_id": "C1", "text": "..."}],
       "documents": [{"title": "Security report", "text": "..."}]}}

Send `material` (inline documents, cut into evidence by intake) or `case` (an
already structured case), never both. File paths are refused. Poll
`GET /judgments/{id}` until `status` is `completed` or `failed`. A completed
judgment with `degraded: true` means the engine could not finish properly and
is asking for human review; it is not a clean decision.

## Limits (env, with defaults)

- `YUKTI_RATE_LIMIT_PER_MINUTE=60` per key
- `YUKTI_MAX_ACTIVE_PER_CLIENT=2`
- `YUKTI_MAX_CONCURRENT_JUDGMENTS=1` across the server. A live judgment makes
  about 7 model calls, so keep this low on a free tier.
- `YUKTI_MAX_REQUEST_BYTES=500000`
- `YUKTI_DB_PATH`, the SQLite file (default `data/yukti.db`)

## Not built yet

HTTPS and deployment, per-client quotas beyond the limits above, key rotation,
idempotency keys, D-Core admission of results, and a hosted database (SQLite on
one server is the deliberate starting point).
