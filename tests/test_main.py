from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ping_returns_pong():
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.json() == "pong"


def test_healthz_returns_ok():
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version_returns_version_and_sha():
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json()["version"]
    assert response.json()["sha"]


def test_metrics_returns_prometheus_metrics():
    client.get("/ping")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "http_requests_total" in response.text
