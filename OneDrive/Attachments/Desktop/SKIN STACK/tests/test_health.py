"""
Test health check endpoint
Following STEP 0 rules: test /healthz returns 200
"""
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_healthz_returns_200(client):
    """Test /healthz returns 200 with ok=true"""
    response = client.get("/healthz")

    # Check status code
    assert response.status_code == 200

    # Check response body
    data = response.json()
    assert data["ok"] is True
    assert "request_id" in data
    assert "latency_ms" in data
    assert data["database"] == "connected"


def test_healthz_contains_required_fields(client):
    """Test /healthz response has all required fields"""
    response = client.get("/healthz")
    data = response.json()

    required_fields = ["ok", "request_id", "latency_ms", "database"]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"