"""SQLite-backed persistent memory and conversation history."""

import json
import logging
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

from atlas.config import settings

logger = logging.getLogger(__name__)

_local = threading.local()


def _get_conn() -> sqlite3.Connection:
    if not hasattr(_local, "conn"):
        db_path = Path(settings.memory_db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        _local.conn = sqlite3.connect(str(db_path))
        _local.conn.row_factory = sqlite3.Row
        _init_tables(_local.conn)
    return _local.conn


def _init_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'fact',
            confidence REAL DEFAULT 0.8,
            embedding TEXT,
            created_at TEXT NOT NULL,
            last_accessed TEXT NOT NULL,
            access_count INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            session_id TEXT DEFAULT 'default'
        );

        CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);
        CREATE INDEX IF NOT EXISTS idx_conv_session ON conversation_history(session_id);
        CREATE INDEX IF NOT EXISTS idx_conv_timestamp ON conversation_history(timestamp);

        CREATE TABLE IF NOT EXISTS shopping_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            quantity TEXT,
            category TEXT DEFAULT 'geral',
            completed INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            completed_at TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_shopping_completed ON shopping_list(completed);
    """)
    conn.commit()


# --- Conversation History ---

def add_message(role: str, content: str, session_id: str = "default") -> None:
    conn = _get_conn()
    conn.execute(
        "INSERT INTO conversation_history (role, content, timestamp, session_id) VALUES (?, ?, ?, ?)",
        (role, content, datetime.utcnow().isoformat(), session_id),
    )
    conn.commit()


def get_history(session_id: str = "default", limit: int = 20) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT role, content FROM conversation_history WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit),
    ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def get_message_count(session_id: str = "default") -> int:
    conn = _get_conn()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM conversation_history WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    return row["cnt"]


def clear_history(session_id: str = "default") -> None:
    conn = _get_conn()
    conn.execute("DELETE FROM conversation_history WHERE session_id = ?", (session_id,))
    conn.commit()


def list_sessions() -> list[dict]:
    """List all sessions with their last activity timestamp."""
    conn = _get_conn()
    rows = conn.execute("""
        SELECT session_id, MAX(timestamp) as last_activity, COUNT(*) as message_count
        FROM conversation_history
        GROUP BY session_id
        ORDER BY last_activity DESC
    """).fetchall()
    return [dict(r) for r in rows]


def cleanup_expired_sessions(expiry_hours: int = 24) -> int:
    """Delete sessions older than expiry_hours. Returns count of deleted sessions."""
    conn = _get_conn()
    cutoff = datetime.utcnow()
    from datetime import timedelta
    cutoff = (cutoff - timedelta(hours=expiry_hours)).isoformat()

    # Find expired sessions
    expired = conn.execute("""
        SELECT session_id FROM conversation_history
        GROUP BY session_id
        HAVING MAX(timestamp) < ?
    """, (cutoff,)).fetchall()

    if not expired:
        return 0

    expired_ids = [r["session_id"] for r in expired]
    placeholders = ",".join("?" * len(expired_ids))
    conn.execute(f"DELETE FROM conversation_history WHERE session_id IN ({placeholders})", expired_ids)
    conn.commit()

    logger.info("Cleaned up %d expired sessions (older than %d hours)", len(expired_ids), expiry_hours)
    return len(expired_ids)


# --- Memories ---

def save_memory(content: str, category: str = "fact", confidence: float = 0.8, embedding: list[float] | None = None) -> int:
    conn = _get_conn()
    now = datetime.utcnow().isoformat()
    emb_json = json.dumps(embedding) if embedding else None
    cursor = conn.execute(
        "INSERT INTO memories (content, category, confidence, embedding, created_at, last_accessed) VALUES (?, ?, ?, ?, ?, ?)",
        (content, category, confidence, emb_json, now, now),
    )
    conn.commit()
    return cursor.lastrowid


def get_all_memories() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM memories ORDER BY last_accessed DESC").fetchall()
    return [dict(r) for r in rows]


def get_memories_by_category(category: str, limit: int = 100) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM memories WHERE category = ? ORDER BY confidence DESC LIMIT ?",
        (category, limit),
    ).fetchall()
    return [dict(r) for r in rows]


def get_recent_memories(limit: int = 20) -> list[dict]:
    """Get most recently accessed memories."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM memories ORDER BY last_accessed DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def get_memories_since(since: datetime) -> list[dict]:
    """Get memories created since a given datetime."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM memories WHERE created_at >= ? ORDER BY created_at DESC",
        (since.isoformat(),),
    ).fetchall()
    return [dict(r) for r in rows]


def add_memory(content: str, category: str = "fact", confidence: float = 0.8) -> int:
    """Alias for save_memory for convenience."""
    return save_memory(content, category, confidence)


def touch_memory(memory_id: int) -> None:
    conn = _get_conn()
    conn.execute(
        "UPDATE memories SET last_accessed = ?, access_count = access_count + 1 WHERE id = ?",
        (datetime.utcnow().isoformat(), memory_id),
    )
    conn.commit()


def delete_memory(memory_id: int) -> None:
    conn = _get_conn()
    conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    conn.commit()


def memory_exists(content: str) -> bool:
    conn = _get_conn()
    row = conn.execute("SELECT 1 FROM memories WHERE content = ? LIMIT 1", (content,)).fetchone()
    return row is not None


# --- Shopping List ---

def add_shopping_item(item: str, quantity: str | None = None, category: str = "geral") -> int:
    """Add item to shopping list. Returns item ID."""
    conn = _get_conn()
    now = datetime.utcnow().isoformat()
    cursor = conn.execute(
        "INSERT INTO shopping_list (item, quantity, category, created_at) VALUES (?, ?, ?, ?)",
        (item, quantity, category, now),
    )
    conn.commit()
    return cursor.lastrowid


def get_shopping_list(include_completed: bool = False) -> list[dict]:
    """Get all shopping list items."""
    conn = _get_conn()
    if include_completed:
        rows = conn.execute(
            "SELECT * FROM shopping_list ORDER BY completed ASC, created_at DESC"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM shopping_list WHERE completed = 0 ORDER BY category, created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def complete_shopping_item(item_id: int) -> bool:
    """Mark item as completed. Returns True if item was found."""
    conn = _get_conn()
    now = datetime.utcnow().isoformat()
    cursor = conn.execute(
        "UPDATE shopping_list SET completed = 1, completed_at = ? WHERE id = ?",
        (now, item_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def uncomplete_shopping_item(item_id: int) -> bool:
    """Mark item as not completed. Returns True if item was found."""
    conn = _get_conn()
    cursor = conn.execute(
        "UPDATE shopping_list SET completed = 0, completed_at = NULL WHERE id = ?",
        (item_id,),
    )
    conn.commit()
    return cursor.rowcount > 0


def delete_shopping_item(item_id: int) -> bool:
    """Delete item from shopping list. Returns True if item was found."""
    conn = _get_conn()
    cursor = conn.execute("DELETE FROM shopping_list WHERE id = ?", (item_id,))
    conn.commit()
    return cursor.rowcount > 0


def clear_completed_shopping() -> int:
    """Remove all completed items. Returns count of deleted items."""
    conn = _get_conn()
    cursor = conn.execute("DELETE FROM shopping_list WHERE completed = 1")
    conn.commit()
    return cursor.rowcount
