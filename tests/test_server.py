from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.server import app, health


client = TestClient(app)


def test_app_is_fastapi_instance():
    assert isinstance(app, FastAPI)


def test_health_function_returns_status_payload():
    assert health() == {"status": "ok"}


def test_health_endpoint_is_json():
    response = client.get("/health")
    assert response.headers["content-type"].startswith("application/json")


def test_health_endpoint_rejects_post():
    response = client.post("/health")
    assert response.status_code == 405


def test_unknown_route_returns_404():
    response = client.get("/does-not-exist")
    assert response.status_code == 404


def test_openapi_schema_exposes_health_route():
    schema = client.get("/openapi.json").json()
    assert "/health" in schema["paths"]
    assert "get" in schema["paths"]["/health"]
