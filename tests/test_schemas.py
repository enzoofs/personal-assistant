"""Tests for atlas.intent.schemas module.

Tests Pydantic model validation and serialization.
"""
import pytest
from pydantic import ValidationError

from atlas.intent.schemas import (
    IntentType,
    IntentResult,
    ActionResult,
    ChatRequest,
    ChatResponse
)


class TestIntentType:
    """Tests for IntentType enum."""

    def test_intent_type_has_all_expected_values(self):
        """Test that IntentType enum has all expected intent types."""
        # Arrange
        expected_intents = [
            "save_note",
            "create_event",
            "query_calendar",
            "log_habit",
            "search",
            "briefing",
            "chat"
        ]

        # Act
        actual_values = [intent.value for intent in IntentType]

        # Assert
        for expected in expected_intents:
            assert expected in actual_values

    def test_intent_type_is_string_enum(self):
        """Test that IntentType values are strings."""
        # Arrange & Act
        intent = IntentType.SAVE_NOTE

        # Assert
        assert isinstance(intent.value, str)
        assert intent.value == "save_note"


class TestIntentResult:
    """Tests for IntentResult Pydantic model."""

    def test_intent_result_with_all_fields(self):
        """Test creating IntentResult with all fields."""
        # Arrange & Act
        result = IntentResult(
            intent=IntentType.SAVE_NOTE,
            parameters={"content": "test", "category": "inbox"},
            confidence=0.95
        )

        # Assert
        assert result.intent == IntentType.SAVE_NOTE
        assert result.parameters == {"content": "test", "category": "inbox"}
        assert result.confidence == 0.95

    def test_intent_result_with_defaults(self):
        """Test that IntentResult has sensible defaults."""
        # Arrange & Act
        result = IntentResult(intent=IntentType.CHAT)

        # Assert
        assert result.parameters == {}
        assert result.confidence == 1.0

    def test_intent_result_accepts_empty_parameters(self):
        """Test IntentResult with empty parameters dict."""
        # Arrange & Act
        result = IntentResult(
            intent=IntentType.BRIEFING,
            parameters={}
        )

        # Assert
        assert result.parameters == {}

    def test_intent_result_validates_confidence_range(self):
        """Test that confidence values outside 0-1 are accepted (no validation)."""
        # Arrange & Act - Pydantic allows any float by default
        result = IntentResult(
            intent=IntentType.CHAT,
            confidence=1.5
        )

        # Assert
        assert result.confidence == 1.5

    def test_intent_result_serialization(self):
        """Test that IntentResult can be serialized to dict."""
        # Arrange
        result = IntentResult(
            intent=IntentType.SAVE_NOTE,
            parameters={"content": "test"},
            confidence=0.8
        )

        # Act
        serialized = result.model_dump()

        # Assert
        assert serialized["intent"] == "save_note"
        assert serialized["parameters"] == {"content": "test"}
        assert serialized["confidence"] == 0.8


class TestActionResult:
    """Tests for ActionResult Pydantic model."""

    def test_action_result_with_all_fields(self):
        """Test creating ActionResult with all fields."""
        # Arrange & Act
        action = ActionResult(
            type="save_note",
            details={
                "path": "inbox/note.md",
                "title": "Test Note",
                "category": "inbox"
            }
        )

        # Assert
        assert action.type == "save_note"
        assert action.details["path"] == "inbox/note.md"
        assert action.details["title"] == "Test Note"

    def test_action_result_with_default_details(self):
        """Test that ActionResult has default empty details."""
        # Arrange & Act
        action = ActionResult(type="search")

        # Assert
        assert action.details == {}

    def test_action_result_accepts_nested_details(self):
        """Test ActionResult with nested details structure."""
        # Arrange & Act
        action = ActionResult(
            type="complex_action",
            details={
                "metadata": {
                    "created": "2026-02-02",
                    "tags": ["test", "example"]
                },
                "count": 42
            }
        )

        # Assert
        assert action.details["metadata"]["created"] == "2026-02-02"
        assert action.details["count"] == 42

    def test_action_result_serialization(self):
        """Test that ActionResult can be serialized to dict."""
        # Arrange
        action = ActionResult(
            type="log_habit",
            details={"habit_type": "exercise", "value": "30"}
        )

        # Act
        serialized = action.model_dump()

        # Assert
        assert serialized["type"] == "log_habit"
        assert serialized["details"]["habit_type"] == "exercise"


class TestChatRequest:
    """Tests for ChatRequest Pydantic model."""

    def test_chat_request_with_message(self):
        """Test creating ChatRequest with message."""
        # Arrange & Act
        request = ChatRequest(message="Hello, ATLAS!")

        # Assert
        assert request.message == "Hello, ATLAS!"

    def test_chat_request_requires_message(self):
        """Test that ChatRequest requires message field."""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError):
            ChatRequest()

    def test_chat_request_accepts_empty_string(self):
        """Test that ChatRequest accepts empty string message."""
        # Arrange & Act
        request = ChatRequest(message="")

        # Assert
        assert request.message == ""

    def test_chat_request_serialization(self):
        """Test that ChatRequest can be serialized to dict."""
        # Arrange
        request = ChatRequest(message="Test message")

        # Act
        serialized = request.model_dump()

        # Assert
        assert serialized["message"] == "Test message"


class TestChatResponse:
    """Tests for ChatResponse Pydantic model."""

    def test_chat_response_with_all_fields(self):
        """Test creating ChatResponse with all fields."""
        # Arrange & Act
        response = ChatResponse(
            response="Here's your answer",
            intent="save_note",
            actions=[
                ActionResult(type="save_note", details={"path": "test.md"})
            ],
            error=None
        )

        # Assert
        assert response.response == "Here's your answer"
        assert response.intent == "save_note"
        assert len(response.actions) == 1
        assert response.error is None

    def test_chat_response_with_defaults(self):
        """Test ChatResponse default values."""
        # Arrange & Act
        response = ChatResponse(
            response="Test response",
            intent="chat"
        )

        # Assert
        assert response.actions == []
        assert response.error is None

    def test_chat_response_with_error(self):
        """Test ChatResponse with error message."""
        # Arrange & Act
        response = ChatResponse(
            response="An error occurred",
            intent="save_note",
            error="Content is required"
        )

        # Assert
        assert response.error == "Content is required"

    def test_chat_response_with_multiple_actions(self):
        """Test ChatResponse with multiple actions."""
        # Arrange
        actions = [
            ActionResult(type="action1", details={"key1": "value1"}),
            ActionResult(type="action2", details={"key2": "value2"}),
            ActionResult(type="action3", details={"key3": "value3"})
        ]

        # Act
        response = ChatResponse(
            response="Multiple actions executed",
            intent="complex",
            actions=actions
        )

        # Assert
        assert len(response.actions) == 3
        assert response.actions[0].type == "action1"
        assert response.actions[2].type == "action3"

    def test_chat_response_serialization(self):
        """Test that ChatResponse can be serialized to dict."""
        # Arrange
        response = ChatResponse(
            response="Test",
            intent="chat",
            actions=[ActionResult(type="test", details={})]
        )

        # Act
        serialized = response.model_dump()

        # Assert
        assert serialized["response"] == "Test"
        assert serialized["intent"] == "chat"
        assert len(serialized["actions"]) == 1
        assert serialized["error"] is None

    def test_chat_response_json_serialization(self):
        """Test that ChatResponse can be serialized to JSON."""
        # Arrange
        response = ChatResponse(
            response="JSON test",
            intent="search",
            actions=[ActionResult(type="search", details={"query": "test"})],
            error=None
        )

        # Act
        json_str = response.model_dump_json()

        # Assert
        assert isinstance(json_str, str)
        assert "JSON test" in json_str
        assert "search" in json_str

    def test_chat_response_with_optional_error_none(self):
        """Test that error can be explicitly set to None."""
        # Arrange & Act
        response = ChatResponse(
            response="Success",
            intent="save_note",
            actions=[],
            error=None
        )

        # Assert
        assert response.error is None
