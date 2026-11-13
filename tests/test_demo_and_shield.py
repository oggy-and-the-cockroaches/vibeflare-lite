"""Tests for Zero-Friction Demo Seeding, Mock Shield Port Gateway, and Offline AI Fallback."""

import pytest
import asyncio
import sqlite3
import json
import urllib.request
import urllib.parse
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.demo_seeder import ensure_demo_project, DEMO_PROJECT_ID
from backend.api.proxy import _local_url, create_proxy_endpoint, disconnect_proxy
from backend.services.llm import get_llm
import backend.database.schema as db_schema


@pytest.fixture
def client():
    return TestClient(app)


def test_local_url_port_parsing():
    """Verify that developers can enter port numbers in multiple formats."""
    assert _local_url("8001") == "http://127.0.0.1:8001"
    assert _local_url(":9000") == "http://127.0.0.1:9000"
    assert _local_url("localhost:5000") == "http://localhost:5000"
    assert _local_url("http://127.0.0.1:8080") == "http://127.0.0.1:8080"


def test_local_url_rejects_dashboard_port():
    """Ensure mock proxy cannot target Shipcheck's own dashboard port 8000."""
    from fastapi import HTTPException
    with pytest.raises(HTTPException):
        _local_url("8000")


@pytest.mark.asyncio
async def test_ensure_demo_project():
    """Verify that ensure_demo_project provisions files and populated database."""
    res = await ensure_demo_project()
    assert res["status"] in ("seeded", "already_seeded")
    assert res["project_id"] == DEMO_PROJECT_ID

    with db_schema.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, security_score FROM projects WHERE id = ?", (DEMO_PROJECT_ID,))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == DEMO_PROJECT_ID

        cursor.execute("SELECT COUNT(*) FROM findings WHERE scan_id IN (SELECT id FROM scans WHERE project_id = ?)", (DEMO_PROJECT_ID,))
        count = cursor.fetchone()[0]
        assert count > 0


def test_seed_demo_api_endpoint(client):
    """Test POST /api/projects/seed-demo endpoint."""
    resp = client.post("/api/projects/seed-demo")
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_id"] == DEMO_PROJECT_ID


def test_explain_finding_offline_fallback():
    """Verify explain_finding produces rich structured output even with no API key."""
    fake_finding = {
        "id": "f-123",
        "title": "SQL Injection in User Search",
        "category": "security",
        "severity": "critical",
        "file_path": "app.py",
        "line_number": 42,
        "evidence": "SELECT * FROM users WHERE id = " + "{user_id}",
        "recommendation": "Use parameterized queries."
    }
    llm = get_llm()
    explanation = llm.explain_finding(fake_finding, "def search(user_id): pass")
    assert isinstance(explanation, dict)
    assert "summary" in explanation
    assert "impact" in explanation
    assert "attack_prerequisites" in explanation
    assert "remediation_guidance" in explanation
    assert "SQL Injection" in explanation["summary"]


def test_settings_api_endpoints(client):
    """Verify user can view, save, and test their Gemini API key and model settings."""
    # 1. GET settings
    res = client.get("/api/settings")
    assert res.status_code == 200
    data = res.json()
    assert "model_name" in data
    assert "gemma-4-31b-it" in data["supported_models"]

    # 2. POST save custom API key and model
    save_res = client.post("/api/settings", json={
        "api_key": "AIzaSyTestMockKeyForGemma4",
        "model_name": "gemma-4-31b-it"
    })
    assert save_res.status_code == 200
    assert save_res.json()["has_api_key"] is True
    assert save_res.json()["model_name"] == "gemma-4-31b-it"

    # 3. Verify settings were persisted and masked in GET
    res2 = client.get("/api/settings")
    assert res2.json()["has_api_key"] is True
    assert "AIzaSy" in res2.json()["masked_key"]

    # 4. Clear key to revert to offline fallback
    clear_res = client.post("/api/settings", json={"api_key": "", "model_name": "gemma-4-31b-it"})
    assert clear_res.status_code == 200
    assert clear_res.json()["has_api_key"] is False


@pytest.mark.asyncio
async def test_mock_shield_port_creation_and_blocking():
    """Test that mock proxy binds an OS port and intercepts attacks with 403."""
    res = await create_proxy_endpoint({"target_url": "8001", "project_id": "test-mock-proj"})
    assert res["success"] is True
    assert res["port"] > 0
    proxy_url = res["proxy_url"]

    # Test SQL injection attack intercepted by mock port
    sqli_url = f"{proxy_url}/api/users?id=1%20OR%201=1--"
    req = urllib.request.Request(sqli_url, method="GET")
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(req, timeout=5)
    assert exc_info.value.code == 403

    # Clean up
    await disconnect_proxy("test-mock-proj")
