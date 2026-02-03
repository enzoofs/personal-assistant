"""Tests for tool handlers in atlas.tools module.

Tests async tool handlers with mocked vault operations.
"""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from atlas.intent.schemas import IntentResult, IntentType, ActionResult
from atlas.tools.obsidian import handle_save_note
from atlas.tools.habits import handle_log_habit, HABIT_CATEGORIES
from atlas.tools.search import handle_search, _web_search
from atlas.tools.briefing import handle_briefing


class TestHandleSaveNote:
    """Tests for handle_save_note tool."""

    @pytest.mark.asyncio
    async def test_handle_save_note_with_valid_content(self, tmp_vault, mock_settings):
        """Test saving a note with valid content."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure
        ensure_vault_structure()

        intent = IntentResult(
            intent=IntentType.SAVE_NOTE,
            parameters={
                "content": "This is my test note content",
                "category": "inbox",
                "tags": ["test"]
            }
        )

        with patch("atlas.vault.manager.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            context, actions = await handle_save_note(intent)

            # Assert
            assert "Nota salva" in context
            assert len(actions) == 1
            assert actions[0].type == "save_note"
            assert "filename" in actions[0].details
            assert actions[0].details["category"] == "inbox"

    @pytest.mark.asyncio
    async def test_handle_save_note_without_content_raises_error(self):
        """Test that saving a note without content raises ValueError."""
        # Arrange
        intent = IntentResult(
            intent=IntentType.SAVE_NOTE,
            parameters={"category": "inbox"}
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Content is required"):
            await handle_save_note(intent)

    @pytest.mark.asyncio
    async def test_handle_save_note_extracts_title_from_markdown_header(self, tmp_vault, mock_settings):
        """Test that title is extracted from markdown header."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure
        ensure_vault_structure()

        intent = IntentResult(
            intent=IntentType.SAVE_NOTE,
            parameters={
                "content": "# My Great Title\n\nSome content here",
                "category": "projects",
                "tags": []
            }
        )

        with patch("atlas.vault.manager.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            context, actions = await handle_save_note(intent)

            # Assert
            assert actions[0].details["title"] == "My Great Title"

    @pytest.mark.asyncio
    async def test_handle_save_note_uses_first_line_as_title_if_no_header(self, tmp_vault, mock_settings):
        """Test that first line is used as title when no markdown header present."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure
        ensure_vault_structure()

        intent = IntentResult(
            intent=IntentType.SAVE_NOTE,
            parameters={
                "content": "Plain text content without header",
                "category": "inbox",
                "tags": []
            }
        )

        with patch("atlas.vault.manager.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            context, actions = await handle_save_note(intent)

            # Assert
            assert "Plain text content without header" in actions[0].details["title"]

    @pytest.mark.asyncio
    async def test_handle_save_note_defaults_to_inbox_category(self, tmp_vault, mock_settings):
        """Test that category defaults to inbox if not provided."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure
        ensure_vault_structure()

        intent = IntentResult(
            intent=IntentType.SAVE_NOTE,
            parameters={"content": "Test content"}
        )

        with patch("atlas.vault.manager.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            context, actions = await handle_save_note(intent)

            # Assert
            assert actions[0].details["category"] == "inbox"

    @pytest.mark.asyncio
    async def test_handle_save_note_adds_reference_to_daily_note(self, tmp_vault, mock_settings):
        """Test that a reference is added to the daily note."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure, read_note
        ensure_vault_structure()

        intent = IntentResult(
            intent=IntentType.SAVE_NOTE,
            parameters={"content": "Important note"}
        )

        with patch("atlas.vault.manager.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            await handle_save_note(intent)

            # Assert - check daily note has reference
            _, daily_content = read_note("daily/2026-02-02.md")
            assert "Important note" in daily_content or "important-note" in daily_content


class TestHandleLogHabit:
    """Tests for handle_log_habit tool."""

    @pytest.mark.asyncio
    async def test_handle_log_habit_with_valid_data(self, tmp_vault, mock_settings):
        """Test logging a habit with valid data."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure
        ensure_vault_structure()

        intent = IntentResult(
            intent=IntentType.LOG_HABIT,
            parameters={
                "type": "exercise",
                "value": "30",
                "unit": "minutes"
            }
        )

        with patch("atlas.tools.habits.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            context, actions = await handle_log_habit(intent)

            # Assert
            assert "Hábito" in context
            assert "exercise" in context
            assert len(actions) == 1
            assert actions[0].type == "log_habit"
            assert actions[0].details["habit_type"] == "exercise"
            assert actions[0].details["value"] == "30"
            assert actions[0].details["unit"] == "minutes"

    @pytest.mark.asyncio
    async def test_handle_log_habit_without_value_raises_error(self):
        """Test that logging habit without value raises ValueError."""
        # Arrange
        intent = IntentResult(
            intent=IntentType.LOG_HABIT,
            parameters={"type": "exercise"}
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Value is required"):
            await handle_log_habit(intent)

    @pytest.mark.asyncio
    async def test_handle_log_habit_saves_to_correct_category(self, tmp_vault, mock_settings):
        """Test that habits are saved to the correct category folder."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure
        ensure_vault_structure()

        intent = IntentResult(
            intent=IntentType.LOG_HABIT,
            parameters={
                "type": "sleep",
                "value": "8",
                "unit": "hours"
            }
        )

        with patch("atlas.tools.habits.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            context, actions = await handle_log_habit(intent)

            # Assert
            assert actions[0].details["path"].startswith("habits/health/")

    @pytest.mark.asyncio
    async def test_handle_log_habit_with_productivity_category(self, tmp_vault, mock_settings):
        """Test logging a productivity habit."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure
        ensure_vault_structure()

        intent = IntentResult(
            intent=IntentType.LOG_HABIT,
            parameters={
                "type": "meditation",
                "value": "15",
                "unit": "minutes"
            }
        )

        with patch("atlas.tools.habits.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            context, actions = await handle_log_habit(intent)

            # Assert
            assert "habits/productivity/" in actions[0].details["path"]

    @pytest.mark.asyncio
    async def test_handle_log_habit_without_unit(self, tmp_vault, mock_settings):
        """Test logging a habit without unit parameter."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure
        ensure_vault_structure()

        intent = IntentResult(
            intent=IntentType.LOG_HABIT,
            parameters={
                "type": "mood",
                "value": "happy"
            }
        )

        with patch("atlas.tools.habits.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            context, actions = await handle_log_habit(intent)

            # Assert
            assert actions[0].details["unit"] == ""

    @pytest.mark.asyncio
    async def test_handle_log_habit_adds_to_daily_note(self, tmp_vault, mock_settings):
        """Test that habit log is added to daily note."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure, read_note
        ensure_vault_structure()

        intent = IntentResult(
            intent=IntentType.LOG_HABIT,
            parameters={
                "type": "water",
                "value": "2",
                "unit": "liters"
            }
        )

        with patch("atlas.tools.habits.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            await handle_log_habit(intent)

            # Assert
            _, daily_content = read_note("daily/2026-02-02.md")
            assert "water" in daily_content
            assert "2" in daily_content


class TestHandleSearch:
    """Tests for handle_search tool."""

    @pytest.mark.asyncio
    async def test_handle_search_without_query_raises_error(self):
        """Test that searching without query raises ValueError."""
        # Arrange
        intent = IntentResult(
            intent=IntentType.SEARCH,
            parameters={}
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Query is required"):
            await handle_search(intent)

    @pytest.mark.asyncio
    async def test_handle_search_vault_only(self, mock_chroma):
        """Test searching vault only."""
        # Arrange
        mock_chroma.query.return_value = {
            "ids": [["note1.md"]],
            "documents": [["Test document content"]],
            "metadatas": [[{"path": "inbox/note1.md", "title": "Test Note"}]],
            "distances": [[0.5]]
        }
        mock_chroma.count.return_value = 1

        intent = IntentResult(
            intent=IntentType.SEARCH,
            parameters={"query": "test query", "source": "vault"}
        )

        # Act
        context, actions = await handle_search(intent)

        # Assert
        assert "Resultados do Vault" in context
        assert len(actions) == 1
        assert actions[0].type == "search"
        assert actions[0].details["vault_count"] >= 0

    @pytest.mark.asyncio
    async def test_handle_search_web_only(self, mock_tavily, mock_settings):
        """Test searching web only."""
        # Arrange
        intent = IntentResult(
            intent=IntentType.SEARCH,
            parameters={"query": "python testing", "source": "web"}
        )

        # Act
        context, actions = await handle_search(intent)

        # Assert
        assert len(actions) == 1
        assert actions[0].details["source"] == "web"

    @pytest.mark.asyncio
    async def test_handle_search_both_sources(self, mock_chroma, mock_tavily, mock_settings):
        """Test searching both vault and web."""
        # Arrange
        mock_chroma.count.return_value = 1
        mock_chroma.query.return_value = {
            "ids": [["note1.md"]],
            "documents": [["Vault content"]],
            "metadatas": [[{"path": "inbox/note1.md", "title": "Vault Note"}]],
            "distances": [[0.3]]
        }

        intent = IntentResult(
            intent=IntentType.SEARCH,
            parameters={"query": "test", "source": "both"}
        )

        # Act
        context, actions = await handle_search(intent)

        # Assert
        assert actions[0].details["source"] == "both"

    @pytest.mark.asyncio
    async def test_handle_search_no_results(self, mock_chroma):
        """Test search with no results."""
        # Arrange
        mock_chroma.count.return_value = 0
        mock_chroma.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }

        intent = IntentResult(
            intent=IntentType.SEARCH,
            parameters={"query": "nonexistent", "source": "vault"}
        )

        # Act
        context, actions = await handle_search(intent)

        # Assert
        assert "Nenhum resultado encontrado" in context


class TestWebSearch:
    """Tests for _web_search helper function."""

    def test_web_search_with_invalid_api_key(self, mock_settings):
        """Test web search with invalid API key returns empty list."""
        # Arrange
        mock_settings.tavily_api_key = "tvly-test"

        # Act
        results = _web_search("test query")

        # Assert
        assert results == []

    def test_web_search_with_missing_api_key(self, mock_settings):
        """Test web search without API key returns empty list."""
        # Arrange
        mock_settings.tavily_api_key = ""

        # Act
        results = _web_search("test query")

        # Assert
        assert results == []


class TestHandleBriefing:
    """Tests for handle_briefing tool."""

    @pytest.mark.asyncio
    async def test_handle_briefing_without_daily_note(self, tmp_vault, mock_settings):
        """Test briefing when no daily note exists."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure
        ensure_vault_structure()

        intent = IntentResult(intent=IntentType.BRIEFING, parameters={})

        with patch("atlas.tools.briefing.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            context, actions = await handle_briefing(intent)

            # Assert
            assert "Briefing" in context
            assert "Nenhuma nota diária" in context
            assert len(actions) == 1
            assert actions[0].type == "briefing"

    @pytest.mark.asyncio
    async def test_handle_briefing_with_daily_note(self, tmp_vault, mock_settings):
        """Test briefing when daily note exists."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure, write_note
        ensure_vault_structure()

        # Create a daily note
        write_note(
            "daily/2026-02-02.md",
            {"date": "2026-02-02", "tags": ["daily"]},
            "# 2026-02-02\n\n## Agenda\n- Meeting at 10am\n\n## Notas\n- Important note"
        )

        intent = IntentResult(intent=IntentType.BRIEFING, parameters={})

        with patch("atlas.tools.briefing.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            context, actions = await handle_briefing(intent)

            # Assert
            assert "Briefing" in context
            assert "Meeting at 10am" in context

    @pytest.mark.asyncio
    async def test_handle_briefing_with_inbox_notes(self, tmp_vault, mock_settings):
        """Test briefing includes recent inbox notes."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure, write_note
        ensure_vault_structure()

        # Create inbox notes
        write_note(
            "inbox/note1.md",
            {"title": "Note 1", "tags": []},
            "Content of note 1"
        )

        intent = IntentResult(intent=IntentType.BRIEFING, parameters={})

        with patch("atlas.tools.briefing.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            context, actions = await handle_briefing(intent)

            # Assert
            assert "Notas Recentes" in context or "Note 1" in context

    @pytest.mark.asyncio
    async def test_handle_briefing_with_todays_habits(self, tmp_vault, mock_settings):
        """Test briefing includes today's habits."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure, write_note
        ensure_vault_structure()

        # Create habit note for today
        write_note(
            "habits/health/2026-02-02-exercise.md",
            {
                "date": "2026-02-02",
                "habit_type": "exercise",
                "value": "30",
                "unit": "minutes",
                "tags": ["habit", "exercise"]
            },
            "# exercise — 2026-02-02\n\n- 10:30: 30 minutes"
        )

        intent = IntentResult(intent=IntentType.BRIEFING, parameters={})

        with patch("atlas.tools.briefing.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            context, actions = await handle_briefing(intent)

            # Assert
            assert "Hábitos de Hoje" in context
            assert "exercise" in context or "30" in context

    @pytest.mark.asyncio
    async def test_handle_briefing_without_habits(self, tmp_vault, mock_settings):
        """Test briefing when no habits are logged."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure
        ensure_vault_structure()

        intent = IntentResult(intent=IntentType.BRIEFING, parameters={})

        with patch("atlas.tools.briefing.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 2, 10, 30)
            mock_dt.strftime = datetime.strftime

            # Act
            context, actions = await handle_briefing(intent)

            # Assert
            assert "Nenhum hábito registrado" in context
