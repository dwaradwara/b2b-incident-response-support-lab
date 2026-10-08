import logging
import uuid

from fastapi import FastAPI, Request


logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

logger = logging.getLogger("session-provider")

app = FastAPI(
    title="Demo Session Provider",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "session-provider",
    }


@app.post("/session")
def create_session(request: Request):
    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid.uuid4()),
    )

    logger.info(
        f'provider_session_created request_id="{request_id}"'
    )

    return {
        "provider_session_id": f"upstream_{uuid.uuid4().hex[:10]}",
        "status": "created",
        "request_id": request_id,
    }
