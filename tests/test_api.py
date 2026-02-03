"""Tests for atlas.main FastAPI application."""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from atlas.config import settings as real_settings
from atlas.main import app
from atlas.intent.schemas import ActionResult


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"X-API-Key": real_settings.atlas_api_key}


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_correct_structure(self, client):
        data = client.get("/health").json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"

    def test_health_no_auth_required(self, client):
        assert client.get("/health").status_code == 200


class TestChatEndpoint:
    def test_requires_api_key(self, client):
        response = client.post("/chat", json={"message": "Hello"})
        assert response.status_code == 401

    def test_rejects_invalid_api_key(self, client):
        response = client.post("/chat", json={"message": "Hello"}, headers={"X-API-Key": "wrong"})
        assert response.status_code == 401

    def test_valid_request(self, client, auth_headers):
        with patch("atlas.main.process", new_callable=AsyncMock) as mock_process:
            mock_process.return_value = ("Response", "chat", [], None)
            response = client.post("/chat", json={"message": "Hello"}, headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Response"
            assert data["intent"] == "chat"
            assert data["actions"] == []
            assert data["error"] is None

    def test_processes_message(self, client, auth_headers):
        with patch("atlas.main.process", new_callable=AsyncMock) as mock_process:
            mock_process.return_value = ("OK", "chat", [], None)
            client.post("/chat", json={"message": "test msg"}, headers=auth_headers)
            mock_process.assert_called_once_with("test msg")

    def test_with_error(self, client, auth_headers):
        with patch("atlas.main.process", new_callable=AsyncMock) as mock_process:
            mock_process.return_value = ("Error", "save_note", [], "Content is required")
            data = client.post("/chat", json={"message": "x"}, headers=auth_headers).json()
            assert data["error"] == "Content is required"

    def test_missing_message_field(self, client, auth_headers):
        response = client.post("/chat", json={}, headers=auth_headers)
        assert response.status_code == 422

    def test_with_actions(self, client, auth_headers):
        actions = [ActionResult(type="save_note", details={"path": "test.md"})]
        with patch("atlas.main.process", new_callable=AsyncMock) as mock_process:
            mock_process.return_value = ("Done", "save_note", actions, None)
            data = client.post("/chat", json={"message": "x"}, headers=auth_headers).json()
            assert len(data["actions"]) == 1
            assert data["actions"][0]["type"] == "save_note"

    def test_returns_utf8(self, client, auth_headers):
        with patch("atlas.main.process", new_callable=AsyncMock) as mock_process:
            mock_process.return_value = ("Olá!", "chat", [], None)
            response = client.post("/chat", json={"message": "oi"}, headers=auth_headers)
            assert "charset=utf-8" in response.headers["content-type"].lower()


class TestAppMetadata:
    def test_app_title(self):
        assert app.title == "ATLAS"

    def test_app_version(self):
        assert app.version == "0.1.0"
