import pytest
from main import app as flask_app


@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def test_index_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_index_json_structure(client):
    data = client.get("/").get_json()
    assert "service" in data
    assert "version" in data
    assert "env" in data


def test_health_returns_healthy(client):
    data = client.get("/health").get_json()
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data


def test_ready_returns_ready(client):
    data = client.get("/ready").get_json()
    assert data["status"] == "ready"


def test_metrics_endpoint(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"app_requests_total" in resp.data
