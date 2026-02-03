from enum import Enum

from pydantic import BaseModel


class IntentType(str, Enum):
    SAVE_NOTE = "save_note"
    CREATE_EVENT = "create_event"
    QUERY_CALENDAR = "query_calendar"
    DELETE_EVENT = "delete_event"
    EDIT_EVENT = "edit_event"
    LOG_HABIT = "log_habit"
    READ_EMAIL = "read_email"
    SEND_EMAIL = "send_email"
    CONFIRM_SEND_EMAIL = "confirm_send_email"
    TRASH_EMAIL = "trash_email"
    SEARCH = "search"
    BRIEFING = "briefing"
    SHOPPING_ADD = "shopping_add"
    SHOPPING_LIST = "shopping_list"
    SHOPPING_COMPLETE = "shopping_complete"
    CHAT = "chat"


class IntentResult(BaseModel):
    intent: IntentType
    parameters: dict = {}
    confidence: float = 1.0


class ActionResult(BaseModel):
    type: str
    details: dict = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    intent: str
    actions: list[ActionResult] = []
    error: str | None = None
