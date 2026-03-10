"""Sleep pattern analyzer."""

import logging
import random
from datetime import datetime, timedelta
from statistics import mean, stdev
from zoneinfo import ZoneInfo

from atlas.config import settings
from atlas.proactive.config import PATTERN_THRESHOLDS, SARCASTIC_TEMPLATES
from atlas.proactive.schemas import (
    AnalysisResult,
    Insight,
    InsightPriority,
    InsightType,
)
from atlas.proactive.insight_store import insight_exists_recent
from atlas.vault.manager import list_notes, read_note

logger = logging.getLogger(__name__)


def _get_sleep_data(days: int = 30) -> list[dict]:
    """Get sleep entries from vault."""
    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz).date()
    entries = []

    try:
        notes = list_notes("habits/health")
        for note_path in notes:
            try:
                fm, _ = read_note(f"habits/health/{note_path.name}")
                if fm.get("habit_type") != "sleep":
                    continue

                date_str = fm.get("date", "")
                value = fm.get("value")

                if date_str and value is not None:
                    note_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if (today - note_date).days <= days:
                        try:
                            hours = float(value)
                            entries.append({
                                "date": note_date,
                                "hours": hours,
                            })
                        except (ValueError, TypeError):
                            continue
            except Exception:
                continue
    except FileNotFoundError:
        pass

    return sorted(entries, key=lambda x: x["date"], reverse=True)


def _get_message(msg_type: str, **kwargs) -> str:
    """Get a random sarcastic sleep message."""
    templates = SARCASTIC_TEMPLATES.get("sleep", {}).get(msg_type, [])
    if not templates:
        return f"Padrão de sono detectado: {msg_type}"
    return random.choice(templates).format(**kwargs)


async def analyze_sleep() -> AnalysisResult:
    """Analyze sleep patterns and generate insights.

    Returns:
        AnalysisResult with insights about sleep trends and irregularities.
    """
    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz)
    date_str = today.strftime("%Y-%m-%d")

    result = AnalysisResult()

    # Get sleep data
    window = PATTERN_THRESHOLDS["sleep_trend_window"]
    sleep_data = _get_sleep_data(days=window * 2)  # Get extra for context

    if len(sleep_data) < 3:
        logger.debug("Not enough sleep data for analysis")
        return result

    # Recent entries for analysis
    recent = sleep_data[:window]
    recent_hours = [e["hours"] for e in recent]

    if not recent_hours:
        return result

    avg_sleep = mean(recent_hours)

    # Check for low sleep average
    if avg_sleep < PATTERN_THRESHOLDS["sleep_low_threshold"]:
        insight_id = f"sleep_low_{date_str}"

        if not insight_exists_recent("sleep_low", hours=48):
            insight = Insight(
                id=insight_id,
                type=InsightType.SLEEP_TREND,
                priority=InsightPriority.NORMAL,
                title="Sono Insuficiente",
                message=_get_message("low", hours=f"{avg_sleep:.1f}"),
                data={
                    "avg_hours": round(avg_sleep, 1),
                    "days_analyzed": len(recent_hours),
                    "threshold": PATTERN_THRESHOLDS["sleep_low_threshold"],
                },
                actions=[],
            )
            result.insights.append(insight)

    # Check for high sleep average
    elif avg_sleep > PATTERN_THRESHOLDS["sleep_high_threshold"]:
        insight_id = f"sleep_high_{date_str}"

        if not insight_exists_recent("sleep_high", hours=48):
            insight = Insight(
                id=insight_id,
                type=InsightType.SLEEP_TREND,
                priority=InsightPriority.LOW,
                title="Sono Excessivo",
                message=_get_message("high", hours=f"{avg_sleep:.1f}"),
                data={
                    "avg_hours": round(avg_sleep, 1),
                    "days_analyzed": len(recent_hours),
                },
                actions=[],
            )
            result.insights.append(insight)

    # Check for irregular sleep (high variance)
    if len(recent_hours) >= 5:
        try:
            sleep_variance = stdev(recent_hours)

            if sleep_variance > PATTERN_THRESHOLDS["sleep_variance_alert"]:
                insight_id = f"sleep_irregular_{date_str}"

                if not insight_exists_recent("sleep_irregular", hours=72):
                    insight = Insight(
                        id=insight_id,
                        type=InsightType.SLEEP_IRREGULAR,
                        priority=InsightPriority.NORMAL,
                        title="Sono Irregular",
                        message=_get_message("irregular", variance=f"{sleep_variance:.1f}"),
                        data={
                            "variance_hours": round(sleep_variance, 1),
                            "min_hours": min(recent_hours),
                            "max_hours": max(recent_hours),
                            "avg_hours": round(avg_sleep, 1),
                        },
                        actions=[],
                    )
                    result.insights.append(insight)
        except Exception:
            pass  # Not enough data for stdev

    # Add trend metadata
    result.metadata = {
        "avg_sleep_hours": round(avg_sleep, 1),
        "entries_analyzed": len(recent_hours),
        "date_range": f"{recent[-1]['date']} to {recent[0]['date']}" if recent else "",
    }

    logger.info("Sleep analysis generated %d insights", len(result.insights))
    return result
