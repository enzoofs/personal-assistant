"""Tests for atlas.orchestrator module.

Tests process function and tool registry.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from atlas.intent.schemas import IntentResult, IntentType, ActionResult
from atlas.orchestrator import register_tool, process, _tool_registry


class TestRegisterTool:
    """Tests for register_tool function."""

    def test_register_tool_adds_handler_to_registry(self):
        """Test that register_tool adds handler to the registry."""
        # Arrange
        async def mock_handler(intent):
            return "context", []

        # Act
        register_tool(IntentType.CHAT, mock_handler)

        # Assert
        assert IntentType.CHAT in _tool_registry
        assert _tool_registry[IntentType.CHAT] == mock_handler

    def test_register_tool_overwrites_existing_handler(self):
        """Test that registering the same intent twice overwrites the handler."""
        # Arrange
        async def first_handler(intent):
            return "first", []

        async def second_handler(intent):
            return "second", []

        # Act
        register_tool(IntentType.SAVE_NOTE, first_handler)
        register_tool(IntentType.SAVE_NOTE, second_handler)

        # Assert
        assert _tool_registry[IntentType.SAVE_NOTE] == second_handler

    def test_register_multiple_tools(self):
        """Test registering multiple different tools."""
        # Arrange
        async def handler1(intent):
            return "handler1", []

        async def handler2(intent):
            return "handler2", []

        # Act
        register_tool(IntentType.LOG_HABIT, handler1)
        register_tool(IntentType.SEARCH, handler2)

        # Assert
        assert IntentType.LOG_HABIT in _tool_registry
        assert IntentType.SEARCH in _tool_registry
        assert _tool_registry[IntentType.LOG_HABIT] == handler1
        assert _tool_registry[IntentType.SEARCH] == handler2


class TestProcess:
    """Tests for process function."""

    @pytest.mark.asyncio
    async def test_process_with_chat_intent_no_handler(self):
        """Test processing a chat intent without a registered handler."""
        # Arrange
        message = "Hello, how are you?"

        with patch("atlas.orchestrator.classify_intent") as mock_classify:
            mock_classify.return_value = IntentResult(
                intent=IntentType.CHAT,
                parameters={},
                confidence=1.0
            )

            with patch("atlas.orchestrator.generate_response") as mock_response:
                mock_response.return_value = "I'm doing well, thanks!"

                # Act
                response, intent, actions, error = await process(message)

                # Assert
                assert response == "I'm doing well, thanks!"
                assert intent == "chat"
                assert actions == []
                assert error is None

    @pytest.mark.asyncio
    async def test_process_with_registered_handler(self, tmp_vault, mock_settings):
        """Test processing with a registered tool handler."""
        # Arrange
        from atlas.vault.manager import ensure_vault_structure
        ensure_vault_structure()

        message = "Save this note"

        # Mock handler
        async def mock_save_handler(intent):
            return "Note saved successfully", [
                ActionResult(type="save_note", details={"path": "test.md"})
            ]

        # Register the handler
        register_tool(IntentType.SAVE_NOTE, mock_save_handler)

        with patch("atlas.orchestrator.classify_intent") as mock_classify:
            mock_classify.return_value = IntentResult(
                intent=IntentType.SAVE_NOTE,
                parameters={"content": "Test note"},
                confidence=0.9
            )

            with patch("atlas.orchestrator.generate_response") as mock_response:
                mock_response.return_value = "Done!"

                # Act
                response, intent, actions, error = await process(message)

                # Assert
                assert intent == "save_note"
                assert len(actions) == 1
                assert actions[0].type == "save_note"
                assert error is None

    @pytest.mark.asyncio
    async def test_process_handler_exception(self):
        """Test that process handles exceptions from tool handlers."""
        # Arrange
        message = "Log my exercise"

        # Mock handler that raises exception
        async def failing_handler(intent):
            raise ValueError("Test error")

        register_tool(IntentType.LOG_HABIT, failing_handler)

        with patch("atlas.orchestrator.classify_intent") as mock_classify:
            mock_classify.return_value = IntentResult(
                intent=IntentType.LOG_HABIT,
                parameters={"type": "exercise"},
                confidence=0.8
            )

            with patch("atlas.orchestrator.generate_response") as mock_response:
                mock_response.return_value = "Sorry, something went wrong"

                # Act
                response, intent, actions, error = await process(message)

                # Assert
                assert intent == "log_habit"
                assert actions == []
                assert error == "Test error"

    @pytest.mark.asyncio
    async def test_process_calls_classify_intent(self):
        """Test that process calls classify_intent with the message."""
        # Arrange
        message = "Test message"

        with patch("atlas.orchestrator.classify_intent") as mock_classify:
            mock_classify.return_value = IntentResult(
                intent=IntentType.CHAT,
                parameters={},
                confidence=1.0
            )

            with patch("atlas.orchestrator.generate_response") as mock_response:
                mock_response.return_value = "Response"

                # Act
                await process(message)

                # Assert
                mock_classify.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_process_calls_generate_response_with_context(self):
        """Test that process passes tool context to generate_response."""
        # Arrange
        message = "Search for something"
        tool_context = "Found 3 results in vault"

        async def mock_search_handler(intent):
            return tool_context, [ActionResult(type="search", details={})]

        register_tool(IntentType.SEARCH, mock_search_handler)

        with patch("atlas.orchestrator.classify_intent") as mock_classify:
            mock_classify.return_value = IntentResult(
                intent=IntentType.SEARCH,
                parameters={"query": "test"},
                confidence=0.9
            )

            with patch("atlas.orchestrator.generate_response") as mock_response:
                mock_response.return_value = "Here are your results"

                # Act
                await process(message)

                # Assert
                mock_response.assert_called_once()
                call_args = mock_response.call_args
                assert call_args[0][0] == message
                assert call_args[0][2] == tool_context  # tool_context is third argument

    @pytest.mark.asyncio
    async def test_process_returns_tuple_with_four_elements(self):
        """Test that process returns a tuple of (response, intent, actions, error)."""
        # Arrange
        message = "Test"

        with patch("atlas.orchestrator.classify_intent") as mock_classify:
            mock_classify.return_value = IntentResult(
                intent=IntentType.CHAT,
                parameters={},
                confidence=1.0
            )

            with patch("atlas.orchestrator.generate_response") as mock_response:
                mock_response.return_value = "Response"

                # Act
                result = await process(message)

                # Assert
                assert isinstance(result, tuple)
                assert len(result) == 4
                response, intent, actions, error = result
                assert isinstance(response, str)
                assert isinstance(intent, str)
                assert isinstance(actions, list)
                assert error is None or isinstance(error, str)

    @pytest.mark.asyncio
    async def test_process_with_briefing_intent(self):
        """Test processing a briefing intent."""
        # Arrange
        message = "What's my briefing?"

        async def mock_briefing_handler(intent):
            return "Today's briefing: ...", [
                ActionResult(type="briefing", details={"date": "2026-02-02"})
            ]

        register_tool(IntentType.BRIEFING, mock_briefing_handler)

        with patch("atlas.orchestrator.classify_intent") as mock_classify:
            mock_classify.return_value = IntentResult(
                intent=IntentType.BRIEFING,
                parameters={},
                confidence=1.0
            )

            with patch("atlas.orchestrator.generate_response") as mock_response:
                mock_response.return_value = "Here's your briefing"

                # Act
                response, intent, actions, error = await process(message)

                # Assert
                assert intent == "briefing"
                assert len(actions) == 1
                assert actions[0].type == "briefing"

    @pytest.mark.asyncio
    async def test_process_with_low_confidence_intent(self):
        """Test processing with low confidence classification."""
        # Arrange
        message = "Maybe save this?"

        with patch("atlas.orchestrator.classify_intent") as mock_classify:
            mock_classify.return_value = IntentResult(
                intent=IntentType.CHAT,
                parameters={},
                confidence=0.3  # Low confidence
            )

            with patch("atlas.orchestrator.generate_response") as mock_response:
                mock_response.return_value = "I'm not sure what you mean"

                # Act
                response, intent, actions, error = await process(message)

                # Assert
                assert intent == "chat"
                assert error is None

    @pytest.mark.asyncio
    async def test_process_handler_returns_multiple_actions(self):
        """Test that process handles multiple actions from a tool."""
        # Arrange
        message = "Do multiple things"

        async def multi_action_handler(intent):
            actions = [
                ActionResult(type="action1", details={"key1": "value1"}),
                ActionResult(type="action2", details={"key2": "value2"}),
                ActionResult(type="action3", details={"key3": "value3"})
            ]
            return "Multiple actions completed", actions

        register_tool(IntentType.SAVE_NOTE, multi_action_handler)

        with patch("atlas.orchestrator.classify_intent") as mock_classify:
            mock_classify.return_value = IntentResult(
                intent=IntentType.SAVE_NOTE,
                parameters={},
                confidence=1.0
            )

            with patch("atlas.orchestrator.generate_response") as mock_response:
                mock_response.return_value = "All done"

                # Act
                response, intent, actions, error = await process(message)

                # Assert
                assert len(actions) == 3
                assert actions[0].type == "action1"
                assert actions[1].type == "action2"
                assert actions[2].type == "action3"
