import json
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.logging_config import RequestLoggingMiddleware
from backend.demo import app as demo


@pytest.mark.parametrize("path,status", [("/ok", 200), ("/missing", 404),
                                         ("/failure", 503), ("/exception", 500)])
def test_completion_is_json_and_safe(path, status, capsys):
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/ok")
    def ok():
        return {"ok": True}

    @app.get("/failure", status_code=503)
    def failure():
        return {"error": True}

    @app.get("/exception")
    def exception():
        raise RuntimeError("secret-password")

    request_id = str(uuid.uuid4())
    response = TestClient(app).get(path + "?token=secret-password", headers={
        "Authorization": "Bearer secret-password", "X-Request-ID": request_id})
    assert response.status_code == status
    raw = capsys.readouterr().out
    records = [json.loads(line) for line in raw.splitlines()]
    assert len(records) == 1
    record = records[0]
    assert record.keys() >= {"timestamp", "severity", "service", "event", "http_method",
                             "http_path", "http_status", "duration_ms", "request_id"}
    assert type(record["http_status"]) is int
    assert record["http_status"] == status
    assert record["duration_ms"] >= 0
    assert record["request_id"] == response.headers["x-request-id"] == request_id
    assert "secret-password" not in raw + response.text


def test_demo_is_controlled(capsys):
    assert TestClient(demo).get("/internal/demo/http-503").status_code == 503
    record = json.loads(capsys.readouterr().out)
    assert record["controlled_failure"] is True
    assert record["severity"] == "ERROR"


def test_untrusted_path_and_request_id_are_not_logged(capsys):
    app = FastAPI()
    app.add_middleware(RequestLoggingMiddleware)
    TestClient(app).get("/secret-password", headers={"x-request-id": "secret-password"})
    raw = capsys.readouterr().out
    assert "secret-password" not in raw
    uuid.UUID(json.loads(raw)["request_id"])
