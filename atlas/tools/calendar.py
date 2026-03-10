"""Google Calendar tool — create and query events."""

import logging

from atlas.intent.schemas import ActionResult, IntentResult, IntentType
from atlas.orchestrator import register_tool
from atlas.services.google_calendar import create_event, delete_event, edit_event, list_events

logger = logging.getLogger(__name__)


async def handle_create_event(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Handle create_event intent."""
    title = intent.parameters.get("title", "")
    dt = intent.parameters.get("datetime", "")
    description = intent.parameters.get("description", "")

    if not title or not dt:
        raise ValueError("Titulo e datetime sao obrigatorios para criar um evento.")

    event = await create_event(title, dt, description)

    context = (
        f"Evento '{title}' criado com sucesso para {event['start']}. "
        f"Link: {event['link']}"
    )

    action = ActionResult(
        type="create_event",
        details={
            "title": title,
            "datetime": event["start"],
            "link": event["link"],
            "event_id": event["id"],
        },
    )

    return context, [action]


async def handle_query_calendar(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Handle query_calendar intent."""
    period = intent.parameters.get("period", "today")

    events = await list_events(period)

    if not events:
        context = f"Nenhum evento encontrado para '{period}'."
    else:
        lines = [f"- {e['start']}: {e['summary']}" for e in events]
        context = f"Eventos para '{period}' ({len(events)}):\n" + "\n".join(lines)

    action = ActionResult(
        type="query_calendar",
        details={
            "period": period,
            "count": len(events),
            "events": events,
        },
    )

    return context, [action]


async def handle_delete_event(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Handle delete_event intent."""
    title = intent.parameters.get("title", "")
    date = intent.parameters.get("date", "")

    if not title or not date:
        raise ValueError("Titulo e data sao obrigatorios para deletar um evento.")

    result = await delete_event(title, date)

    context = f"Evento '{result['summary']}' em {result['date']} foi deletado com sucesso."

    action = ActionResult(
        type="delete_event",
        details={
            "title": result["summary"],
            "date": result["date"],
            "event_id": result["id"],
        },
    )

    return context, [action]


async def handle_edit_event(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Handle edit_event intent."""
    title = intent.parameters.get("title", "")
    date = intent.parameters.get("date", "")

    if not title or not date:
        raise ValueError("Titulo e data do evento original sao obrigatorios para editar.")

    result = await edit_event(
        title=title,
        date=date,
        new_title=intent.parameters.get("new_title"),
        new_datetime=intent.parameters.get("new_datetime"),
        new_description=intent.parameters.get("new_description"),
    )

    context = f"Evento atualizado: '{result['summary']}' em {result['start']}."

    action = ActionResult(
        type="edit_event",
        details={
            "title": result["summary"],
            "start": result["start"],
            "event_id": result["id"],
        },
    )

    return context, [action]


register_tool(IntentType.CREATE_EVENT, handle_create_event)
register_tool(IntentType.QUERY_CALENDAR, handle_query_calendar)
register_tool(IntentType.DELETE_EVENT, handle_delete_event)
register_tool(IntentType.EDIT_EVENT, handle_edit_event)
