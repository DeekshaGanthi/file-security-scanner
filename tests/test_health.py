from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.health import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_liveness_has_no_database_dependency():
    with patch("backend.health.check_database", side_effect=RuntimeError("offline")) as db:
        assert client.get("/health/live").json() == {"status": "alive"}
        db.assert_not_called()


def test_readiness_checks_database():
    with patch("backend.health.check_database") as db:
        assert client.get("/health/ready").status_code == 200
        db.assert_called_once()


def test_database_outage_does_not_fail_liveness_or_leak_details():
    with patch("backend.health.check_database", side_effect=RuntimeError("secret-password")):
        response = client.get("/health/ready")
        assert response.status_code == 503
        assert response.json() == {"status": "not_ready", "database": "unavailable"}
        assert "secret-password" not in response.text
        assert client.get("/health/live").status_code == 200
