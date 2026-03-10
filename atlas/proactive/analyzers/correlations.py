"""Cross-data correlation analyzer."""

import logging
import random
from datetime import datetime, timedelta
from statistics import mean
from zoneinfo import ZoneInfo

from atlas.config import settings
from atlas.proactive.config import SARCASTIC_TEMPLATES
from atlas.proactive.schemas import (
    AnalysisResult,
    Insight,
    InsightPriority,
    InsightType,
)
from atlas.proactive.insight_store import insight_exists_recent
from atlas.vault.manager import list_notes, read_note

logger = logging.getLogger(__name__)


def _get_habit_data(days: int = 30) -> dict[str, list[dict]]:
    """Get all habit data organized by type."""
    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz).date()
    data: dict[str, list[dict]] = {}

    folders = ["habits/health", "habits/productivity"]

    for folder in folders:
        try:
            notes = list_notes(folder)
            for note_path in notes:
                try:
                    fm, _ = read_note(f"{folder}/{note_path.name}")
                    date_str = fm.get("date", "")
                    habit_type = fm.get("habit_type", "")
                    value = fm.get("value")

                    if date_str and habit_type:
                        note_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                        if (today - note_date).days <= days:
                            if habit_type not in data:
                                data[habit_type] = []
                            data[habit_type].append({
                                "date": note_date,
                                "value": value,
                            })
                except Exception:
                    continue
        except FileNotFoundError:
            continue

    return data


def _get_message(correlation_type: str, **kwargs) -> str:
    """Get correlation message."""
    templates = SARCASTIC_TEMPLATES.get("correlation", {}).get(correlation_type, [])
    if not templates:
        return f"Correlação detectada: {correlation_type}"
    return random.choice(templates).format(**kwargs)


async def analyze_correlations() -> AnalysisResult:
    """Analyze correlations between different data sources.

    Returns:
        AnalysisResult with correlation insights.
    """
    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz)
    date_str = today.strftime("%Y-%m-%d")

    result = AnalysisResult()

    # Get habit data
    habit_data = _get_habit_data(days=30)

    # Need sleep and exercise data for correlation
    sleep_data = habit_data.get("sleep", [])
    exercise_data = habit_data.get("exercise", [])

    if len(sleep_data) >= 7 and len(exercise_data) >= 5:
        # Analyze sleep quality on exercise days vs non-exercise days
        exercise_dates = set(e["date"] for e in exercise_data if e["value"])

        sleep_with_exercise = []
        sleep_without_exercise = []

        for sleep in sleep_data:
            try:
                hours = float(sleep["value"])
                # Check if exercised the day before
                prev_day = sleep["date"] - timedelta(days=1)
                if prev_day in exercise_dates:
                    sleep_with_exercise.append(hours)
                else:
                    sleep_without_exercise.append(hours)
            except (ValueError, TypeError):
                continue

        # Calculate averages
        if len(sleep_with_exercise) >= 3 and len(sleep_without_exercise) >= 3:
            avg_with = mean(sleep_with_exercise)
            avg_without = mean(sleep_without_exercise)

            # If sleep is better after exercise days
            if avg_with > avg_without + 0.3:  # At least 0.3h difference
                insight_id = f"correlation_sleep_exercise_{date_str}"

                if not insight_exists_recent("correlation_sleep_exercise", hours=168):  # Once a week
                    insight = Insight(
                        id=insight_id,
                        type=InsightType.CORRELATION,
                        priority=InsightPriority.LOW,
                        title="Padrão Detectado",
                        message=_get_message("sleep_exercise"),
                        data={
                            "avg_sleep_with_exercise": round(avg_with, 1),
                            "avg_sleep_without": round(avg_without, 1),
                            "improvement": round(avg_with - avg_without, 1),
                            "sample_size": len(sleep_with_exercise) + len(sleep_without_exercise),
                        },
                        actions=[],
                    )
                    result.insights.append(insight)

    # Add other correlations as we get more data types...

    logger.info("Correlation analysis generated %d insights", len(result.insights))
    return result
