import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build

from atlas.config import settings
from atlas.services.google_auth import get_credentials

logger = logging.getLogger(__name__)


def _get_service():
    """Build Google Calendar API service."""
    return build("calendar", "v3", credentials=get_credentials())


def _tz() -> ZoneInfo:
    return ZoneInfo(settings.timezone)


async def create_event(
    title: str,
    dt: str,
    description: str = "",
) -> dict:
    """Create a calendar event.

    Args:
        title: Event summary/title.
        dt: ISO 8601 datetime string.
        description: Optional event description.

    Returns:
        Dict with event id, link, start, and summary.
    """
    service = _get_service()

    start = datetime.fromisoformat(dt).replace(tzinfo=_tz())
    end = start + timedelta(hours=1)

    event_body = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start.isoformat(), "timeZone": settings.timezone},
        "end": {"dateTime": end.isoformat(), "timeZone": settings.timezone},
    }

    event = service.events().insert(calendarId="primary", body=event_body).execute()
    logger.info("Event created: %s", event.get("htmlLink"))

    return {
        "id": event["id"],
        "link": event.get("htmlLink", ""),
        "start": start.isoformat(),
        "summary": title,
    }


async def list_events(period: str = "today") -> list[dict]:
    """List calendar events for a given period.

    Args:
        period: One of 'today', 'tomorrow', 'week'.

    Returns:
        List of event dicts with start, summary, and id.
    """
    service = _get_service()
    tz = _tz()
    now = datetime.now(tz)

    if period == "tomorrow":
        day_start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
    elif period == "week":
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=7)
    else:  # today
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=day_start.isoformat(),
            timeMax=day_end.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = []
    for item in result.get("items", []):
        start = item["start"].get("dateTime", item["start"].get("date", ""))
        events.append({
            "id": item["id"],
            "summary": item.get("summary", "(sem titulo)"),
            "start": start,
        })

    return events


async def delete_event(title: str, date: str) -> dict:
    """Delete a calendar event by title and date.

    Searches for events on the given date matching the title, deletes the first match.

    Args:
        title: Event title to search for.
        date: Date string YYYY-MM-DD.

    Returns:
        Dict with deleted event info or error.
    """
    service = _get_service()
    tz = _tz()

    day_start = datetime.fromisoformat(f"{date}T00:00:00").replace(tzinfo=tz)
    day_end = day_start + timedelta(days=1)

    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=day_start.isoformat(),
            timeMax=day_end.isoformat(),
            singleEvents=True,
            q=title,
        )
        .execute()
    )

    items = result.get("items", [])
    if not items:
        raise ValueError(f"Nenhum evento encontrado com titulo '{title}' em {date}.")

    event = items[0]
    service.events().delete(calendarId="primary", eventId=event["id"]).execute()
    logger.info("Event deleted: %s (%s)", event.get("summary"), event["id"])

    return {
        "id": event["id"],
        "summary": event.get("summary", ""),
        "date": date,
    }


async def edit_event(
    title: str,
    date: str,
    new_title: str | None = None,
    new_datetime: str | None = None,
    new_description: str | None = None,
) -> dict:
    """Edit a calendar event by title and date.

    Searches for the event, then updates the provided fields.

    Args:
        title: Current event title to search for.
        date: Date string YYYY-MM-DD of the event.
        new_title: New title (optional).
        new_datetime: New ISO 8601 datetime (optional).
        new_description: New description (optional).

    Returns:
        Dict with updated event info.
    """
    service = _get_service()
    tz = _tz()

    day_start = datetime.fromisoformat(f"{date}T00:00:00").replace(tzinfo=tz)
    day_end = day_start + timedelta(days=1)

    result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=day_start.isoformat(),
            timeMax=day_end.isoformat(),
            singleEvents=True,
            q=title,
        )
        .execute()
    )

    items = result.get("items", [])
    if not items:
        raise ValueError(f"Nenhum evento encontrado com titulo '{title}' em {date}.")

    event = items[0]
    update_body: dict = {}

    if new_title:
        update_body["summary"] = new_title
    if new_description is not None:
        update_body["description"] = new_description
    if new_datetime:
        start = datetime.fromisoformat(new_datetime).replace(tzinfo=tz)
        end = start + timedelta(hours=1)
        update_body["start"] = {"dateTime": start.isoformat(), "timeZone": settings.timezone}
        update_body["end"] = {"dateTime": end.isoformat(), "timeZone": settings.timezone}

    if not update_body:
        raise ValueError("Nenhum campo para atualizar foi fornecido.")

    updated = (
        service.events()
        .patch(calendarId="primary", eventId=event["id"], body=update_body)
        .execute()
    )
    logger.info("Event updated: %s (%s)", updated.get("summary"), updated["id"])

    new_start = updated["start"].get("dateTime", updated["start"].get("date", ""))
    return {
        "id": updated["id"],
        "summary": updated.get("summary", ""),
        "start": new_start,
    }
