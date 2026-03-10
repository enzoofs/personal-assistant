"""Habit pattern analyzer."""

import logging
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from atlas.config import settings
from atlas.proactive.config import PATTERN_THRESHOLDS, SARCASTIC_TEMPLATES
from atlas.proactive.schemas import (
    AnalysisResult,
    Insight,
    InsightAction,
    InsightPriority,
    InsightType,
)
from atlas.proactive.insight_store import insight_exists_recent
from atlas.vault.manager import list_notes, read_note

logger = logging.getLogger(__name__)


def _get_habit_entries(habit_folder: str, days: int = 30) -> list[dict]:
    """Get habit entries from vault."""
    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz).date()
    entries = []

    try:
        notes = list_notes(habit_folder)
        for note_path in notes:
            try:
                fm, _ = read_note(f"{habit_folder}/{note_path.name}")
                date_str = fm.get("date", "")
                if date_str:
                    note_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if (today - note_date).days <= days:
                        entries.append({
                            "date": note_date,
                            "type": fm.get("habit_type", note_path.stem),
                            "value": fm.get("value"),
                            "unit": fm.get("unit", ""),
                        })
            except Exception:
                continue
    except FileNotFoundError:
        pass

    return sorted(entries, key=lambda x: x["date"], reverse=True)


def _calculate_gap(entries: list[dict], habit_type: str) -> int:
    """Calculate days since last entry."""
    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz).date()

    filtered = [e for e in entries if e["type"] == habit_type]
    if not filtered:
        return 999

    return (today - filtered[0]["date"]).days


def _calculate_streak(entries: list[dict], habit_type: str) -> int:
    """Calculate current consecutive days streak."""
    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz).date()

    filtered = sorted(
        [e for e in entries if e["type"] == habit_type],
        key=lambda x: x["date"],
        reverse=True,
    )

    if not filtered:
        return 0

    streak = 0
    expected = today

    for entry in filtered:
        if entry["date"] == expected:
            streak += 1
            expected -= timedelta(days=1)
        elif entry["date"] < expected:
            break

    return streak


def _get_message(category: str, msg_type: str, **kwargs) -> str:
    """Get a random sarcastic message."""
    templates = SARCASTIC_TEMPLATES.get(category, {}).get(msg_type, [])
    if not templates:
        templates = SARCASTIC_TEMPLATES.get("generic", {}).get(msg_type, [""])

    return random.choice(templates).format(**kwargs)


async def analyze_habits() -> AnalysisResult:
    """Analyze habit patterns and generate insights.

    Returns:
        AnalysisResult with insights about habit gaps and streaks.
    """
    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz)
    date_str = today.strftime("%Y-%m-%d")

    result = AnalysisResult()

    # Get all habit entries
    health_entries = _get_habit_entries("habits/health", days=30)
    productivity_entries = _get_habit_entries("habits/productivity", days=30)
    all_entries = health_entries + productivity_entries

    # Track which habits exist in the vault
    known_habits = set(e["type"] for e in all_entries)

    # Analyze each known habit type
    for habit_type in known_habits:
        gap = _calculate_gap(all_entries, habit_type)
        streak = _calculate_streak(all_entries, habit_type)

        # Check for gap warning
        if gap >= PATTERN_THRESHOLDS["habit_gap_warning"]:
            insight_id = f"habit_gap_{habit_type}_{date_str}"

            # Skip if similar insight exists recently
            if insight_exists_recent(f"habit_gap_{habit_type}", hours=24):
                continue

            priority = (
                InsightPriority.HIGH
                if gap >= PATTERN_THRESHOLDS["habit_gap_critical"]
                else InsightPriority.NORMAL
            )

            # Get template category (default to generic)
            category = habit_type if habit_type in SARCASTIC_TEMPLATES else "generic"

            insight = Insight(
                id=insight_id,
                type=InsightType.HABIT_GAP,
                priority=priority,
                title=habit_type.replace("_", " ").title(),
                message=_get_message(category, "gap", days=gap, habit=habit_type),
                data={"habit": habit_type, "days_since_last": gap},
                actions=[
                    InsightAction(
                        label="Registrar",
                        intent="log_habit",
                        parameters={"habit": habit_type, "value": True},
                    )
                ],
            )
            result.insights.append(insight)

        # Check for streak celebration
        elif streak >= PATTERN_THRESHOLDS["habit_streak_celebrate"]:
            insight_id = f"habit_streak_{habit_type}_{date_str}"

            if insight_exists_recent(f"habit_streak_{habit_type}", hours=48):
                continue

            category = habit_type if habit_type in SARCASTIC_TEMPLATES else "generic"

            insight = Insight(
                id=insight_id,
                type=InsightType.HABIT_STREAK,
                priority=InsightPriority.LOW,
                title="Parabéns!",
                message=_get_message(category, "streak", days=streak, habit=habit_type),
                data={"habit": habit_type, "streak_days": streak},
                actions=[],
            )
            result.insights.append(insight)

    logger.info("Habit analysis generated %d insights", len(result.insights))
    return result
