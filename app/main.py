import json
import logging
import os
import time
import uuid
from importlib.metadata import PackageNotFoundError, version

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest


logger = logging.getLogger("insiderone")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests.",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["method", "path"],
)


def get_package_version() -> str:
    try:
        return version("insiderone-devops-app")
    except PackageNotFoundError:
        return os.getenv("APP_VERSION", "0.1.0")


app = FastAPI(
    title="InsiderOne DevOps Case Study",
    version=get_package_version(),
)


@app.middleware("http")
async def observe_requests(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    started_at = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration = time.perf_counter() - started_at
        path = request.url.path

        if path != "/metrics":
            REQUEST_COUNT.labels(
                method=request.method,
                path=path,
                status=str(status_code),
            ).inc()
            REQUEST_LATENCY.labels(
                method=request.method,
                path=path,
            ).observe(duration)

        logger.info(
            json.dumps(
                {
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "level": "info",
                    "msg": "request_completed",
                    "request_id": request_id,
                    "method": request.method,
                    "path": path,
                    "status": status_code,
                    "duration_ms": round(duration * 1000, 2),
                }
            )
        )


@app.get("/ping")
def ping() -> str:
    return "pong"


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/version")
def app_version() -> dict[str, str]:
    return {
        "version": get_package_version(),
        "sha": os.getenv("GIT_SHA", "local"),
    }


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
