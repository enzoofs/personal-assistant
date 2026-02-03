"""Persistent conversation history backed by SQLite."""

from atlas.memory.store import (
    add_message as _db_add,
    clear_history as _db_clear,
    get_history as _db_get,
    get_message_count as _db_count,
    list_sessions as _db_list_sessions,
    cleanup_expired_sessions as _db_cleanup,
)


def add_message(role: str, content: str, session_id: str = "default") -> None:
    _db_add(role, content, session_id=session_id)


def get_history(session_id: str = "default", limit: int = 20) -> list[dict]:
    return _db_get(session_id=session_id, limit=limit)


def get_message_count(session_id: str = "default") -> int:
    return _db_count(session_id=session_id)


def clear(session_id: str = "default") -> None:
    _db_clear(session_id=session_id)


def list_sessions() -> list[dict]:
    return _db_list_sessions()


def cleanup_expired_sessions(expiry_hours: int = 24) -> int:
    return _db_cleanup(expiry_hours=expiry_hours)
