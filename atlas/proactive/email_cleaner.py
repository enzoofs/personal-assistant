"""Background email triage — reads new emails, trashes junk, flags important ones."""

import asyncio
import json
import logging
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from atlas.config import settings
from atlas.memory.store import save_memory
from atlas.services.gmail import list_emails, trash_email
from atlas.services.openai_client import chat_completion

logger = logging.getLogger(__name__)

TRIAGE_INTERVAL = 1800  # 30 minutes
_MAX_RETRIES = 3

# Track already-processed email IDs so we don't re-triage
_processed_ids: set[str] = set()

# Learned sender cache: sender_address -> "trash" | "keep"
_sender_cache: dict[str, str] = {}

# Accumulated alerts for the dashboard/briefing
email_alerts: list[dict] = []

TRIAGE_PROMPT = """\
Você é um triador de emails. Analise o email abaixo e classifique-o.

De: {from_}
Assunto: {subject}
Prévia: {snippet}

Responda APENAS com JSON válido:
{{
  "action": "trash" | "keep",
  "important": true | false,
  "category": "spam" | "newsletter" | "promotion" | "payment" | "meeting" | "work" | "personal" | "notification" | "other",
  "summary": "resumo curto em português (1 frase)",
  "reason": "por que essa decisão"
}}

Regras:
- "trash": newsletters, promoções, spam, notificações automáticas sem valor
- "keep": emails de pessoas reais, pagamentos, cobranças, reuniões, trabalho, faculdade
- "important": true para pagamentos, cobranças com prazo, reuniões, mensagens pessoais diretas
- Seja agressivo em deletar lixo, mas conservador com coisas potencialmente importantes
"""


def _extract_address(from_field: str) -> str:
    """Extract email address from 'Name <email>' format."""
    match = re.search(r"<(.+?)>", from_field)
    return match.group(1).lower() if match else from_field.lower().strip()


async def _call_with_retry(coro_func, *args, **kwargs):
    """Call an async function with exponential backoff retry."""
    for attempt in range(_MAX_RETRIES):
        try:
            return await coro_func(*args, **kwargs)
        except Exception as e:
            if attempt == _MAX_RETRIES - 1:
                raise
            wait = 2 ** (attempt + 1)
            logger.warning("Retry %d/%d after error: %s (wait %ds)", attempt + 1, _MAX_RETRIES, e, wait)
            await asyncio.sleep(wait)


async def _triage_email(email: dict) -> dict | None:
    """Use LLM to classify a single email. Returns triage result or None on error."""
    try:
        raw = await _call_with_retry(
            chat_completion,
            messages=[{
                "role": "user",
                "content": TRIAGE_PROMPT.format(
                    from_=email["from"],
                    subject=email["subject"],
                    snippet=email.get("snippet", ""),
                ),
            }],
            temperature=0.1,
        )
        return json.loads(raw)
    except (json.JSONDecodeError, Exception) as e:
        logger.warning("Triage failed for email %s: %s", email["id"], e)
        return None


async def _triage_once() -> dict:
    """Run one triage pass on unread emails."""
    stats = {"trashed": 0, "kept": 0, "important": 0, "cached": 0}

    try:
        emails = await _call_with_retry(list_emails, query="is:unread", max_results=20)
    except Exception as exc:
        logger.error("Failed to fetch emails after retries: %s", exc)
        return stats

    if not emails:
        return stats

    for email in emails:
        if email["id"] in _processed_ids:
            continue

        _processed_ids.add(email["id"])
        sender = _extract_address(email["from"])

        # Check sender cache first — skip LLM call
        if sender in _sender_cache:
            cached_action = _sender_cache[sender]
            if cached_action == "trash":
                try:
                    await trash_email(email["id"])
                    stats["trashed"] += 1
                    stats["cached"] += 1
                    logger.info("Auto-trashed (cached): %s — %s", email["from"], email["subject"])
                except Exception:
                    logger.warning("Failed to trash cached email %s", email["id"])
                continue
            else:
                stats["kept"] += 1
                stats["cached"] += 1
                continue

        # LLM triage
        result = await _triage_email(email)

        if not result:
            stats["kept"] += 1
            continue

        # Learn sender for future emails
        action = result.get("action", "keep")
        category = result.get("category", "other")
        # Only cache senders with consistent categories (not personal/work which vary)
        if category in ("spam", "newsletter", "promotion", "notification"):
            _sender_cache[sender] = "trash"
        elif category in ("personal", "work"):
            _sender_cache[sender] = "keep"

        if action == "trash":
            try:
                await trash_email(email["id"])
                stats["trashed"] += 1
                logger.info("Auto-trashed [%s]: %s — %s", category, email["from"], email["subject"])
            except Exception:
                logger.warning("Failed to trash email %s", email["id"])
        else:
            stats["kept"] += 1

            if result.get("important"):
                stats["important"] += 1
                alert = {
                    "email_id": email["id"],
                    "from": email["from"],
                    "subject": email["subject"],
                    "category": category,
                    "summary": result.get("summary", ""),
                    "timestamp": datetime.now(ZoneInfo(settings.timezone)).isoformat(),
                }
                email_alerts.append(alert)
                logger.info("IMPORTANT email [%s]: %s — %s", category, email["from"], alert["summary"])

                try:
                    save_memory(
                        content=f"Email importante de {email['from']}: {alert['summary']}",
                        category="email",
                    )
                except Exception:
                    pass

    # Cap caches to avoid unbounded growth
    if len(_processed_ids) > 500:
        _processed_ids.clear()
    if len(_sender_cache) > 200:
        # Keep only the most recent half
        items = list(_sender_cache.items())
        _sender_cache.clear()
        _sender_cache.update(items[-100:])

    return stats


def get_email_alerts(limit: int = 10) -> list[dict]:
    """Get recent important email alerts (for dashboard/briefing)."""
    return email_alerts[-limit:]


def clear_email_alerts() -> None:
    """Clear alerts after they've been shown."""
    email_alerts.clear()


async def start_email_triage() -> None:
    """Long-running background loop for email triage."""
    logger.info("Email triage started (interval=%ds)", TRIAGE_INTERVAL)
    while True:
        try:
            stats = await _triage_once()
            if stats["trashed"] or stats["important"]:
                logger.info(
                    "Email triage: trashed=%d, kept=%d, important=%d, cached=%d",
                    stats["trashed"], stats["kept"], stats["important"], stats["cached"],
                )
        except Exception:
            logger.exception("Email triage iteration failed")
        await asyncio.sleep(TRIAGE_INTERVAL)
