import logging
from datetime import datetime

import zoneinfo

from atlas.config import settings
from atlas.intent.schemas import ActionResult, IntentResult, IntentType
from atlas.orchestrator import register_tool
from atlas.vault.manager import append_to_daily_note, write_note
from atlas.vault.templates import note_template

logger = logging.getLogger(__name__)

HABIT_CATEGORIES = {
    "sleep": "habits/health",
    "exercise": "habits/health",
    "mood": "habits/health",
    "water": "habits/health",
    "meditation": "habits/productivity",
    "reading": "habits/productivity",
    "study": "habits/productivity",
    "custom": "habits/health",
}


async def handle_log_habit(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Handle log_habit intent.

    Args:
        intent: IntentResult with parameters

    Returns:
        Tuple of (context_string_for_persona, list_of_actions)
    """
    habit_type = intent.parameters.get("type", "custom")
    value = intent.parameters.get("value", "")
    unit = intent.parameters.get("unit", "")

    if not value:
        raise ValueError("Value is required for logging a habit")

    tz = zoneinfo.ZoneInfo(settings.timezone)
    now = datetime.now(tz)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    # Build habit entry text
    entry_parts = [f"**{habit_type}**"]
    if value:
        entry_parts.append(str(value))
    if unit:
        entry_parts.append(unit)
    entry_text = " — ".join(entry_parts)

    # Append to daily note under Hábitos section
    daily_entry = f"- [{time_str}] {entry_text}"
    append_to_daily_note("## Hábitos", daily_entry)

    # Also save a structured note in habits folder
    category = HABIT_CATEGORIES.get(habit_type, "habits/health")
    filename = f"{date_str}-{habit_type}.md"
    note_path = f"{category}/{filename}"

    tags = ["habit", habit_type]
    frontmatter_data, template_content = note_template(
        f"{habit_type} — {date_str}", category, tags
    )
    frontmatter_data["habit_type"] = habit_type
    frontmatter_data["value"] = value
    if unit:
        frontmatter_data["unit"] = unit

    content = template_content + f"- {time_str}: {value}"
    if unit:
        content += f" {unit}"
    content += "\n"

    write_note(note_path, frontmatter_data, content)

    context = f"Hábito '{habit_type}' registrado: {value} {unit}. Salvo em '{note_path}' e na nota diária."

    action = ActionResult(
        type="log_habit",
        details={
            "habit_type": habit_type,
            "value": value,
            "unit": unit,
            "path": note_path,
            "date": date_str,
        },
    )

    logger.info("Logged habit: %s = %s %s", habit_type, value, unit)

    return context, [action]


register_tool(IntentType.LOG_HABIT, handle_log_habit)
