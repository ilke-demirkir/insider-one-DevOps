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
