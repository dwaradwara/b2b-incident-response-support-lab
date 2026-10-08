import json
import logging
import os
import time
import uuid

import httpx
import psycopg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, make_asgi_app


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

logger = logging.getLogger("incident-lab")

app = FastAPI(
    title="B2B Incident Response Support Lab",
    version="1.0.0",
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://incident:incident@db:5432/incidentlab",
)

VALID_ACCESS_TOKEN = os.getenv(
    "VALID_ACCESS_TOKEN",
    "valid-demo-token",
)

UPSTREAM_SESSION_URL = os.getenv(
    "UPSTREAM_SESSION_URL",
    "http://session-provider:9000/session",
)

REQUEST_COUNT = Counter(
    "incident_lab_http_requests_total",
    "HTTP requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "incident_lab_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
)

app.mount("/metrics", make_asgi_app())


def get_connection():
    return psycopg.connect(DATABASE_URL)


@app.middleware("http")
async def request_observability(request: Request, call_next):
    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid.uuid4()),
    )

    request.state.request_id = request_id
    started = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - started

    response.headers["X-Request-ID"] = request_id

    REQUEST_COUNT.labels(
        request.method,
        request.url.path,
        response.status_code,
    ).inc()

    REQUEST_LATENCY.labels(
        request.method,
        request.url.path,
    ).observe(duration)

    logger.info(
        json.dumps(
            {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            }
        )
    )

    return response


@app.get("/health")
def health():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()

        return {
            "status": "ok",
            "service": "incident-support-api",
            "database": "connected",
        }

    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "database": "unavailable",
            },
        )


@app.get("/api/v1/account")
def account(
    request: Request,
):
    authorization = request.headers.get("Authorization")

    expected = f"Bearer {VALID_ACCESS_TOKEN}"

    if authorization != expected:
        logger.warning(
            json.dumps(
                {
                    "request_id": request.state.request_id,
                    "event": "authentication_failed",
                    "reason": "invalid_or_expired_token",
                }
            )
        )

        return JSONResponse(
            status_code=401,
            content={
                "error": "unauthorized",
                "message": "Invalid or expired access token",
                "request_id": request.state.request_id,
            },
        )

    return {
        "account_id": "acct_demo_001",
        "name": "Acme Gaming",
        "status": "active",
        "request_id": request.state.request_id,
    }


@app.post("/api/v1/session")
def create_session(request: Request):
    try:
        response = httpx.post(
            UPSTREAM_SESSION_URL,
            headers={
                "X-Request-ID": request.state.request_id,
            },
            timeout=2.0,
        )

        response.raise_for_status()

        upstream = response.json()

    except httpx.RequestError as exc:
        logger.error(
            json.dumps(
                {
                    "request_id": request.state.request_id,
                    "event": "session_creation_failed",
                    "reason": "upstream_connection_failure",
                    "upstream": UPSTREAM_SESSION_URL,
                    "error_type": type(exc).__name__,
                    "severity": "critical",
                }
            )
        )

        return JSONResponse(
            status_code=503,
            content={
                "error": "service_unavailable",
                "message": "Session provider is unavailable",
                "request_id": request.state.request_id,
            },
        )

    except httpx.HTTPStatusError as exc:
        logger.error(
            json.dumps(
                {
                    "request_id": request.state.request_id,
                    "event": "session_creation_failed",
                    "reason": "upstream_http_error",
                    "upstream_status": exc.response.status_code,
                    "severity": "critical",
                }
            )
        )

        return JSONResponse(
            status_code=503,
            content={
                "error": "service_unavailable",
                "message": "Session provider returned an error",
                "request_id": request.state.request_id,
            },
        )

    return {
        "session_id": f"sess_{uuid.uuid4().hex[:10]}",
        "status": "created",
        "upstream_session_id": upstream["provider_session_id"],
        "request_id": request.state.request_id,
    }


@app.get("/api/v1/admin/providers/{provider_id}")
def get_provider_config(provider_id: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    provider_id,
                    provider_name,
                    callback_enabled,
                    region,
                    updated_at
                FROM provider_config
                WHERE provider_id = %s
                """,
                (provider_id,),
            )

            row = cur.fetchone()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": "provider_not_found",
                "provider_id": provider_id,
            },
        )

    return {
        "provider_id": row[0],
        "provider_name": row[1],
        "callback_enabled": row[2],
        "region": row[3],
        "updated_at": row[4].isoformat(),
    }


@app.post("/api/v1/admin/providers/{provider_id}/callback")
async def update_provider_callback(
    provider_id: str,
    request: Request,
):
    body = await request.json()

    enabled = body.get("enabled")

    if not isinstance(enabled, bool):
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_request",
                "message": "'enabled' must be true or false",
            },
        )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE provider_config
                SET callback_enabled = %s,
                    updated_at = now()
                WHERE provider_id = %s
                RETURNING
                    provider_id,
                    provider_name,
                    callback_enabled,
                    region,
                    updated_at
                """,
                (
                    enabled,
                    provider_id,
                ),
            )

            row = cur.fetchone()

        conn.commit()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": "provider_not_found",
                "provider_id": provider_id,
            },
        )

    logger.info(
        json.dumps(
            {
                "request_id": request.state.request_id,
                "event": "provider_configuration_updated",
                "provider_id": provider_id,
                "callback_enabled": enabled,
            }
        )
    )

    return {
        "provider_id": row[0],
        "provider_name": row[1],
        "callback_enabled": row[2],
        "region": row[3],
        "updated_at": row[4].isoformat(),
        "request_id": request.state.request_id,
    }


@app.post("/api/v1/provider/session")
def create_provider_session(request: Request):
    provider_id = "provider_demo_001"

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    provider_name,
                    callback_enabled,
                    region
                FROM provider_config
                WHERE provider_id = %s
                """,
                (provider_id,),
            )

            row = cur.fetchone()

    if row is None:
        return JSONResponse(
            status_code=500,
            content={
                "error": "provider_configuration_missing",
                "request_id": request.state.request_id,
            },
        )

    provider_name, callback_enabled, region = row

    if not callback_enabled:
        logger.warning(
            json.dumps(
                {
                    "request_id": request.state.request_id,
                    "event": "provider_session_failed",
                    "provider_id": provider_id,
                    "reason": "callback_disabled",
                    "region": region,
                }
            )
        )

        return JSONResponse(
            status_code=403,
            content={
                "error": "integration_error",
                "message": "Provider callback is disabled",
                "provider_id": provider_id,
                "request_id": request.state.request_id,
            },
        )

    return {
        "session_id": f"provider_sess_{uuid.uuid4().hex[:10]}",
        "provider_id": provider_id,
        "provider_name": provider_name,
        "region": region,
        "status": "created",
        "request_id": request.state.request_id,
    }
