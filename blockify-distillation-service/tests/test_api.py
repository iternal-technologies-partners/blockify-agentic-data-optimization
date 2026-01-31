"""Tests for the FastAPI application."""

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint():
    """Test simple health endpoint."""
    from app.api import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint():
    """Test root endpoint returns service info."""
    from app.api import app

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data


def test_docs_available():
    """Test OpenAPI docs are available."""
    from app.api import app

    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
