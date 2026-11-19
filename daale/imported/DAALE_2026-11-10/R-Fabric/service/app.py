"""The authenticated HTTP API.

Run:  uvicorn "service.app:create_app_from_env" --factory --host 127.0.0.1 --port 8000
(Put HTTPS in front of it: Caddy or nginx. The service itself speaks plain HTTP.)

A judgment takes minutes with a live model, so ``POST /v1/judgments`` returns
202 with an id and the caller polls ``GET /v1/judgments/{id}``. Results are
stored in SQLite and survive a restart; a job that was mid-flight at restart is
reported as failed rather than left looking active forever.
"""

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from daale.intake import IntakeError, build_case
from daale.pipeline import DaalePipeline, budget_shortfall
from daale.providers import (
    build_live_client,
    env_bool,
    fallback_by_kernel_from_env,
    model_by_kernel_from_env,
    provider_name,
)
from daale.validation import DaaleValidationError, validate_case_and_policy

from .security import RateLimiter
from .store import Store

logger = logging.getLogger("daale.service")

ROOT = Path(__file__).resolve().parents[1]
DEGRADED_RULE = "DEGRADED-EXECUTION"


class JudgmentRequest(BaseModel):
    """Exactly one of ``case`` (already structured) or ``material`` (inline documents)."""

    model_config = ConfigDict(extra="forbid")

    policy_id: str
    case: Optional[dict] = None
    material: Optional[dict] = None


def load_policies(directory):
    policies = {}
    for path in sorted(Path(directory).glob("*.json")):
        policy = json.loads(path.read_text(encoding="utf-8"))
        policies[policy["policy_id"]] = policy
    return policies


def _token_totals(trace):
    calls = trace.get("model_calls", {})
    tokens = sum(int((call.get("usage") or {}).get("total_tokens") or 0) for call in calls.values())
    return len(calls), tokens


def create_app(
    store,
    client,
    model_by_kernel,
    policies,
    native_json_schema=False,
    fallback_by_kernel=None,
    isolate_evidence=False,
    provider="unknown",
    cors_origins=(),
    max_concurrent=1,
    max_active_per_client=2,
    rate_per_minute=60,
    max_body_bytes=500_000,
    enable_docs=False,
):
    app = FastAPI(
        title="YUKTI engine",
        docs_url="/docs" if enable_docs else None,
        redoc_url=None,
        openapi_url="/openapi.json" if enable_docs else None,
    )
    limiter = RateLimiter(rate_per_minute)
    executor = ThreadPoolExecutor(max_workers=max_concurrent, thread_name_prefix="judgment")
    app.state.store = store
    app.state.executor = executor

    interrupted = store.mark_interrupted()
    if interrupted:
        logger.warning("marked %d judgment(s) interrupted by the previous shutdown", interrupted)

    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(cors_origins),
            allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type"],
            allow_credentials=False,
        )

    @app.middleware("http")
    async def limit_body(request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH"):
            length = request.headers.get("content-length")
            if length is None or not length.isdigit():
                return JSONResponse({"detail": "Content-Length is required"}, status_code=411)
            if int(length) > max_body_bytes:
                return JSONResponse(
                    {"detail": f"Request body exceeds {max_body_bytes} bytes"}, status_code=413
                )
        return await call_next(request)

    def authenticate(request: Request):
        scheme, _, token = request.headers.get("authorization", "").partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            raise HTTPException(401, "Missing bearer key", headers={"WWW-Authenticate": "Bearer"})
        identity = store.authenticate(token.strip())
        if identity is None:
            raise HTTPException(401, "Invalid or revoked key", headers={"WWW-Authenticate": "Bearer"})
        allowed, retry_after = limiter.allow(identity.key_id)
        if not allowed:
            raise HTTPException(429, "Rate limit exceeded", headers={"Retry-After": str(retry_after)})
        return identity

    # -- open ----------------------------------------------------------------

    @app.get("/v1/health")
    def health():
        return {
            "status": "ok",
            "provider": provider,
            "model": model_by_kernel.get("default"),
            "policies": sorted(policies),
        }

    # -- judgments -----------------------------------------------------------

    def run_judgment(judgment_id, case, policy):
        store.mark_running(judgment_id)
        try:
            pipeline = DaalePipeline(
                client=client,
                model_by_kernel=model_by_kernel,
                native_json_schema=native_json_schema,
                fallback_by_kernel=fallback_by_kernel,
                isolate_evidence=isolate_evidence,
            )
            result = pipeline.run(case, policy)
            calls, tokens = _token_totals(result.trace)
            store.mark_completed(judgment_id, result.decision_packet, result.trace, calls, tokens)
            logger.info("%s completed: %s", judgment_id, result.decision_packet["policy_state"])
        except Exception as error:  # noqa: BLE001 - recorded, never raised into the pool
            logger.exception("%s failed", judgment_id)
            store.mark_failed(judgment_id, f"{type(error).__name__}: {error}")

    @app.post("/v1/judgments", status_code=202)
    def create_judgment(body: JudgmentRequest, identity=Depends(authenticate)):
        if (body.case is None) == (body.material is None):
            raise HTTPException(422, "Send exactly one of 'case' or 'material'")
        policy = policies.get(body.policy_id)
        if policy is None:
            raise HTTPException(422, f"Unknown policy_id; available: {sorted(policies)}")

        try:
            case = body.case if body.case is not None else build_case(
                body.material, None, allow_paths=False
            )
            validate_case_and_policy(case, policy)
        except (IntakeError, DaaleValidationError) as error:
            raise HTTPException(422, str(error)) from error

        shortfall = budget_shortfall(client, model_by_kernel, fallback_by_kernel=fallback_by_kernel)
        if shortfall is not None:
            model, remaining, needed = shortfall
            reset = getattr(client, "budget_reset_seconds", lambda m: 3600)(model)
            raise HTTPException(
                429,
                f"The daily request budget for {model} has {remaining} left and a judgment needs "
                f"at least {needed}. It resets in about {reset // 3600}h {reset % 3600 // 60}m.",
                headers={"Retry-After": str(reset)},
            )

        if store.count_active(identity.client_id) >= max_active_per_client:
            raise HTTPException(
                429,
                f"At most {max_active_per_client} judgments may be active at once; wait for one to finish",
                headers={"Retry-After": "30"},
            )

        judgment_id = store.create_judgment(
            identity.client_id, case, body.policy_id, model_by_kernel.get("default")
        )
        executor.submit(run_judgment, judgment_id, case, policy)
        return {
            "judgment_id": judgment_id,
            "case_id": case["case_id"],
            "status": "queued",
            "poll": f"/v1/judgments/{judgment_id}",
        }

    def present(row):
        decision = row.get("decision")
        if decision is not None:
            row["degraded"] = decision["triggered_rule"]["rule_id"] == DEGRADED_RULE
        return row

    @app.get("/v1/judgments")
    def list_judgments(limit: int = Query(50, ge=1, le=200), identity=Depends(authenticate)):
        return {"judgments": [present(r) for r in store.list_judgments(identity.client_id, limit=limit)]}

    @app.get("/v1/judgments/{judgment_id}")
    def get_judgment(judgment_id: str, identity=Depends(authenticate)):
        row = store.get_judgment(identity.client_id, judgment_id)
        if row is None:
            raise HTTPException(404, "No such judgment")
        return present(row)

    @app.get("/v1/judgments/{judgment_id}/audit")
    def get_audit(judgment_id: str, identity=Depends(authenticate)):
        """The full record: case, prompts, model calls, findings, gap report."""
        row = store.get_judgment(identity.client_id, judgment_id, with_trace=True)
        if row is None:
            raise HTTPException(404, "No such judgment")
        if row["trace"] is None:
            raise HTTPException(409, f"No audit record yet (status: {row['status']})")
        return {"judgment_id": judgment_id, "trace": row["trace"]}

    # -- cases (a case is the set of judgments sharing a case_id) ------------

    @app.get("/v1/cases")
    def list_cases(identity=Depends(authenticate)):
        return {"cases": store.list_cases(identity.client_id)}

    @app.get("/v1/cases/{case_id}")
    def get_case(case_id: str, identity=Depends(authenticate)):
        rows = store.list_judgments(identity.client_id, case_id=case_id, limit=200)
        if not rows:
            raise HTTPException(404, "No such case")
        return {"case_id": case_id, "judgments": [present(r) for r in rows]}

    # -- usage ---------------------------------------------------------------

    @app.get("/v1/usage")
    def usage(identity=Depends(authenticate)):
        return store.usage(identity.client_id)

    return app


def create_app_from_env():
    load_dotenv(ROOT / ".env")
    logging.basicConfig(
        level=os.getenv("DAALE_LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(name)s %(message)s",
        datefmt="%H:%M:%S",
    )
    env = os.environ
    client, native = build_live_client(env)
    origins = [o.strip() for o in env.get("YUKTI_CORS_ORIGINS", "").split(",") if o.strip()]
    return create_app(
        store=Store(env.get("YUKTI_DB_PATH") or ROOT / "data" / "yukti.db"),
        client=client,
        model_by_kernel=model_by_kernel_from_env(env, live=True),
        policies=load_policies(ROOT / "policies"),
        native_json_schema=native,
        fallback_by_kernel=fallback_by_kernel_from_env(env),
        isolate_evidence=env_bool(env, "DAALE_EVIDENCE_SEPARATION"),
        provider=provider_name(env),
        cors_origins=origins,
        max_concurrent=int(env.get("YUKTI_MAX_CONCURRENT_JUDGMENTS", "1")),
        max_active_per_client=int(env.get("YUKTI_MAX_ACTIVE_PER_CLIENT", "2")),
        rate_per_minute=int(env.get("YUKTI_RATE_LIMIT_PER_MINUTE", "60")),
        max_body_bytes=int(env.get("YUKTI_MAX_REQUEST_BYTES", "500000")),
        enable_docs=env.get("YUKTI_ENABLE_DOCS", "").strip().lower() in {"1", "true", "yes"},
    )
