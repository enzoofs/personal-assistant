"""FastAPI endpoint for mobile dashboard data aggregation."""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from googleapiclient.errors import HttpError as GoogleHttpError
from openai import OpenAIError

from atlas.config import settings
from atlas.errors import GoogleServiceError, VaultError
from atlas.memory.store import get_all_memories, get_history
from atlas.services.gmail import list_emails
from atlas.services.google_calendar import list_events
from atlas.vault.manager import get_daily_note_path, list_notes, read_note
from atlas.proactive.email_cleaner import get_email_alerts
from atlas.proactive.insights import generate_insights
from atlas.vault.stats import get_vault_stats

logger = logging.getLogger(__name__)


async def get_dashboard_data() -> dict:
    """Aggregate data for mobile dashboard.

    Returns:
        Dict containing:
            - events: list of today's calendar events
            - habits: list of today's habits from vault
            - vault: vault statistics
            - recent_messages: last 5 conversation messages
            - date: today's date string (YYYY-MM-DD)
    """
    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz)
    date_str = now.strftime("%Y-%m-%d")

    dashboard_data = {
        "date": date_str,
        "events": [],
        "habits": [],
        "vault": {},
        "recent_messages": [],
        "emails": [],
        "memories": [],
        "insights": [],
    }

    # 1. Calendar events - async call with error handling
    try:
        events = await list_events(period="today")
        dashboard_data["events"] = events
        logger.info("Fetched %d calendar events", len(events))
    except GoogleHttpError as e:
        logger.error("Google Calendar API error: %s (status=%s)", e.reason, e.status_code)
        dashboard_data["events"] = []
    except Exception as e:
        logger.exception("Unexpected error fetching calendar events")
        dashboard_data["events"] = []

    # 2. Today's habits - check habits folders for notes with today's date
    try:
        health_notes = list_notes("habits/health")
        productivity_notes = list_notes("habits/productivity")
        today_habits = [
            n for n in health_notes + productivity_notes if date_str in n.name
        ]

        habits_list = []
        for note_path in today_habits:
            folder = (
                "habits/health"
                if note_path.parent.name == "health"
                else "habits/productivity"
            )
            relative = f"{folder}/{note_path.name}"
            try:
                fm, content = read_note(relative)
                habit_data = {
                    "type": fm.get("habit_type", note_path.stem),
                    "value": fm.get("value", ""),
                    "unit": fm.get("unit", ""),
                    "category": folder.split("/")[-1],  # health or productivity
                }
                habits_list.append(habit_data)
            except Exception as e:
                logger.warning("Failed to read habit note %s: %s", relative, e)
                continue

        dashboard_data["habits"] = habits_list
        logger.info("Fetched %d habits for today", len(habits_list))
    except FileNotFoundError as e:
        logger.warning("Habits directory not found: %s", e)
        dashboard_data["habits"] = []
    except Exception as e:
        logger.exception("Unexpected error fetching habits")
        dashboard_data["habits"] = []

    # 3. Vault statistics
    try:
        vault_stats = get_vault_stats()
        dashboard_data["vault"] = vault_stats
        logger.info("Fetched vault stats: %d total notes", vault_stats.get("total_notes", 0))
    except FileNotFoundError:
        logger.warning("Vault path not found, skipping stats")
        dashboard_data["vault"] = {}
    except Exception as e:
        logger.exception("Unexpected error fetching vault stats")
        dashboard_data["vault"] = {}

    # 4. Recent conversation messages
    try:
        messages = get_history(limit=5)
        dashboard_data["recent_messages"] = messages
        logger.info("Fetched %d recent messages", len(messages))
    except Exception as e:
        logger.exception("Database error fetching conversation history")
        dashboard_data["recent_messages"] = []

    # 5. Recent emails
    try:
        emails = await list_emails(query="is:unread", max_results=5)
        dashboard_data["emails"] = emails
    except GoogleHttpError as e:
        logger.error("Gmail API error: %s (status=%s)", e.reason, e.status_code)
        dashboard_data["emails"] = []
    except Exception as e:
        logger.exception("Unexpected error fetching emails")
        dashboard_data["emails"] = []

    # 6. Important email alerts from auto-triage
    try:
        dashboard_data["email_alerts"] = get_email_alerts(limit=10)
    except Exception as e:
        logger.exception("Error fetching email alerts")
        dashboard_data["email_alerts"] = []

    # 7. Recent memories
    try:
        all_mems = get_all_memories()
        sorted_mems = sorted(all_mems, key=lambda m: m.get("last_accessed", ""), reverse=True)
        dashboard_data["memories"] = [
            {"content": m["content"], "category": m["category"]}
            for m in sorted_mems[:10]
        ]
    except Exception as e:
        logger.exception("Database error fetching memories")
        dashboard_data["memories"] = []

    # 8. Proactive insights (Phase 2)
    try:
        dashboard_data["insights"] = await generate_insights()
        logger.info("Generated %d insights", len(dashboard_data["insights"]))
    except Exception as e:
        logger.exception("Error generating insights")
        dashboard_data["insights"] = []

    return dashboard_data
