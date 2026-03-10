import logging
from datetime import datetime

import zoneinfo

from atlas.config import settings
from atlas.intent.schemas import ActionResult, IntentResult, IntentType
from atlas.orchestrator import register_tool
from atlas.proactive.email_cleaner import get_email_alerts
from atlas.vault.manager import get_daily_note_path, list_notes, read_note

logger = logging.getLogger(__name__)


async def handle_briefing(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Handle briefing intent — aggregate daily note, recent notes, and habits.

    Args:
        intent: IntentResult with parameters

    Returns:
        Tuple of (context_string_for_persona, list_of_actions)
    """
    tz = zoneinfo.ZoneInfo(settings.timezone)
    now = datetime.now(tz)
    date_str = now.strftime("%Y-%m-%d")

    context_parts = [f"**Briefing para {date_str}:**\n"]

    # 1. Daily note content
    daily_path = get_daily_note_path()
    try:
        _, daily_content = read_note(str(daily_path))
        context_parts.append("### Nota Diária")
        context_parts.append(daily_content.strip())
    except FileNotFoundError:
        context_parts.append("### Nota Diária")
        context_parts.append("Nenhuma nota diária para hoje ainda.")

    # 2. Recent notes from inbox
    inbox_notes = list_notes("inbox")
    if inbox_notes:
        context_parts.append("\n### Notas Recentes (Inbox)")
        for note_path in inbox_notes[-5:]:  # last 5
            relative = f"inbox/{note_path.name}"
            try:
                fm, content = read_note(relative)
                title = fm.get("title", note_path.stem)
                snippet = content.strip()[:100]
                context_parts.append(f"- **{title}**: {snippet}")
            except Exception:
                continue

    # 3. Today's habits
    health_notes = list_notes("habits/health")
    productivity_notes = list_notes("habits/productivity")
    today_habits = [
        n for n in health_notes + productivity_notes if date_str in n.name
    ]
    if today_habits:
        context_parts.append("\n### Hábitos de Hoje")
        for note_path in today_habits:
            folder = "habits/health" if note_path.parent.name == "health" else "habits/productivity"
            relative = f"{folder}/{note_path.name}"
            try:
                fm, content = read_note(relative)
                habit_type = fm.get("habit_type", note_path.stem)
                value = fm.get("value", "")
                unit = fm.get("unit", "")
                context_parts.append(f"- **{habit_type}**: {value} {unit}".strip())
            except Exception:
                continue
    else:
        context_parts.append("\n### Hábitos de Hoje")
        context_parts.append("Nenhum hábito registrado hoje.")

    # 4. Important email alerts
    alerts = get_email_alerts(limit=5)
    if alerts:
        context_parts.append("\n### Emails Importantes")
        for a in alerts:
            context_parts.append(f"- **[{a['category']}]** {a['from']}: {a['summary']}")
    else:
        context_parts.append("\n### Emails Importantes")
        context_parts.append("Nenhum email importante pendente.")

    context = "\n".join(context_parts)

    action = ActionResult(
        type="briefing",
        details={"date": date_str},
    )

    logger.info("Generated briefing for %s", date_str)

    return context, [action]


register_tool(IntentType.BRIEFING, handle_briefing)
