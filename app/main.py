import os
from importlib.metadata import PackageNotFoundError, version

from fastapi import FastAPI


def get_package_version() -> str:
    try:
        return version("insiderone-devops-app")
    except PackageNotFoundError:
        return os.getenv("APP_VERSION", "0.1.0")


app = FastAPI(
    title="InsiderOne DevOps Case Study",
    version=get_package_version(),
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
