"""Pytest configuration and shared fixtures for ATLAS tests."""
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from atlas.config import settings as real_settings


@pytest.fixture
def tmp_vault(tmp_path):
    """Create a temporary vault directory for testing."""
    vault_path = tmp_path / "vault"
    vault_path.mkdir()
    return vault_path


@pytest.fixture
def mock_settings(tmp_vault):
    """Temporarily override real settings with test values."""
    original_vault = real_settings.vault_path
    original_chroma = real_settings.chroma_db_path
    original_timezone = real_settings.timezone

    real_settings.vault_path = str(tmp_vault)
    real_settings.chroma_db_path = str(tmp_vault.parent / "chroma_db")
    real_settings.timezone = "America/Sao_Paulo"

    yield real_settings

    real_settings.vault_path = original_vault
    real_settings.chroma_db_path = original_chroma
    real_settings.timezone = original_timezone


@pytest.fixture
def mock_openai():
    """Mock OpenAI client to avoid real API calls."""
    with patch("atlas.services.openai_client.chat_completion") as mock:
        mock.return_value = AsyncMock(return_value="Mocked response")
        yield mock


@pytest.fixture
def mock_chroma():
    """Mock ChromaDB client to avoid real database operations."""
    mock_collection = MagicMock()
    mock_collection.count.return_value = 0
    mock_collection.query.return_value = {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]]
    }

    with patch("atlas.vault.indexer.get_collection") as mock:
        mock.return_value = mock_collection
        yield mock_collection


@pytest.fixture
def mock_tavily():
    """Mock Tavily client to avoid real web searches."""
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "results": [
            {
                "title": "Test Result 1",
                "url": "https://example.com/1",
                "content": "This is test content from the web search."
            }
        ]
    }

    with patch("atlas.tools.search.TavilyClient") as mock:
        mock.return_value = mock_client
        yield mock_client
