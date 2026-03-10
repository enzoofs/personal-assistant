"""SQLite persistence for insights."""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from atlas.config import settings
from atlas.proactive.schemas import Insight, InsightCreate, InsightPriority, InsightType

logger = logging.getLogger(__name__)

# Use same database as memory store
DB_PATH = Path(settings.vault_path).parent / "memory.db"


def _get_connection() -> sqlite3.Connection:
    """Get database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_table():
    """Create insights table if not exists."""
    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                priority TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                data TEXT NOT NULL,
                actions TEXT NOT NULL,
                created_at TEXT NOT NULL,
                dismissed INTEGER DEFAULT 0,
                notified INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(type)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_insights_created ON insights(created_at)
        """)
        conn.commit()
    finally:
        conn.close()


# Initialize table on module load
_ensure_table()


def save_insight(insight: Insight) -> bool:
    """Save or update an insight.

    Returns:
        True if new insight was created, False if updated existing.
    """
    conn = _get_connection()
    try:
        # Check if exists
        existing = conn.execute(
            "SELECT id FROM insights WHERE id = ?", (insight.id,)
        ).fetchone()

        if existing:
            conn.execute("""
                UPDATE insights SET
                    priority = ?,
                    message = ?,
                    data = ?,
                    actions = ?
                WHERE id = ?
            """, (
                insight.priority,
                insight.message,
                json.dumps(insight.data),
                json.dumps([a.model_dump() for a in insight.actions]),
                insight.id,
            ))
            conn.commit()
            return False
        else:
            conn.execute("""
                INSERT INTO insights (id, type, priority, title, message, data, actions, created_at, dismissed, notified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                insight.id,
                insight.type,
                insight.priority,
                insight.title,
                insight.message,
                json.dumps(insight.data),
                json.dumps([a.model_dump() for a in insight.actions]),
                insight.created_at.isoformat(),
                1 if insight.dismissed else 0,
                1 if insight.notified else 0,
            ))
            conn.commit()
            return True
    finally:
        conn.close()


def get_active_insights(limit: int = 10) -> list[Insight]:
    """Get non-dismissed insights, most recent first."""
    conn = _get_connection()
    try:
        rows = conn.execute("""
            SELECT * FROM insights
            WHERE dismissed = 0
            ORDER BY
                CASE priority
                    WHEN 'high' THEN 0
                    WHEN 'normal' THEN 1
                    ELSE 2
                END,
                created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [_row_to_insight(row) for row in rows]
    finally:
        conn.close()


def get_insights_by_type(insight_type: InsightType, days: int = 7) -> list[Insight]:
    """Get insights of a specific type from the last N days."""
    conn = _get_connection()
    try:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        rows = conn.execute("""
            SELECT * FROM insights
            WHERE type = ? AND created_at > ?
            ORDER BY created_at DESC
        """, (insight_type, cutoff)).fetchall()

        return [_row_to_insight(row) for row in rows]
    finally:
        conn.close()


def dismiss_insight(insight_id: str) -> bool:
    """Mark an insight as dismissed."""
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "UPDATE insights SET dismissed = 1 WHERE id = ?",
            (insight_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def mark_notified(insight_id: str) -> bool:
    """Mark an insight as notified (push sent)."""
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "UPDATE insights SET notified = 1 WHERE id = ?",
            (insight_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def insight_exists_recent(insight_id_prefix: str, hours: int = 24) -> bool:
    """Check if a similar insight was created recently (dedup)."""
    conn = _get_connection()
    try:
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        row = conn.execute("""
            SELECT 1 FROM insights
            WHERE id LIKE ? AND created_at > ?
            LIMIT 1
        """, (f"{insight_id_prefix}%", cutoff)).fetchone()

        return row is not None
    finally:
        conn.close()


def cleanup_old_insights(days: int = 30):
    """Delete insights older than N days."""
    conn = _get_connection()
    try:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        cursor = conn.execute(
            "DELETE FROM insights WHERE created_at < ? AND dismissed = 1",
            (cutoff,)
        )
        conn.commit()
        logger.info("Cleaned up %d old insights", cursor.rowcount)
    finally:
        conn.close()


def _row_to_insight(row: sqlite3.Row) -> Insight:
    """Convert database row to Insight model."""
    from atlas.proactive.schemas import InsightAction

    data = json.loads(row["data"])
    actions_data = json.loads(row["actions"])
    actions = [InsightAction(**a) for a in actions_data]

    return Insight(
        id=row["id"],
        type=row["type"],
        priority=row["priority"],
        title=row["title"],
        message=row["message"],
        data=data,
        actions=actions,
        created_at=datetime.fromisoformat(row["created_at"]),
        dismissed=bool(row["dismissed"]),
        notified=bool(row["notified"]),
    )
