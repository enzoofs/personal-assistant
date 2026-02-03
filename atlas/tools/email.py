"""Email tool — read and send emails via Gmail."""

import logging

from atlas.intent.schemas import ActionResult, IntentResult, IntentType
from atlas.orchestrator import register_tool
from atlas.services.gmail import get_email, list_emails, send_email, trash_email

logger = logging.getLogger(__name__)

# Pending email awaiting confirmation
_pending_email: dict | None = None


async def handle_read_email(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Handle read_email intent."""
    query = intent.parameters.get("query", "is:unread")
    max_results = intent.parameters.get("max_results", 5)

    emails = await list_emails(query=query, max_results=max_results)

    if not emails:
        context = "Nenhum email encontrado."
    else:
        lines = []
        for e in emails:
            lines.append(f"- De: {e['from']} | Assunto: {e['subject']} | {e['snippet'][:100]}")
        context = f"Emails encontrados ({len(emails)}):\n" + "\n".join(lines)

    action = ActionResult(
        type="read_email",
        details={
            "query": query,
            "count": len(emails),
            "emails": emails,
        },
    )

    return context, [action]


async def handle_send_email(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Stage email for confirmation instead of sending immediately."""
    global _pending_email

    to = intent.parameters.get("to", "")
    subject = intent.parameters.get("subject", "")
    body = intent.parameters.get("body", "")

    if not to or not subject:
        raise ValueError("Destinatário e assunto são obrigatórios para enviar email.")

    _pending_email = {"to": to, "subject": subject, "body": body}

    context = (
        f"Email preparado (aguardando confirmação):\n"
        f"**Para:** {to}\n"
        f"**Assunto:** {subject}\n"
        f"**Corpo:** {body[:200]}\n\n"
        f"Diga 'confirma' ou 'pode enviar' para enviar."
    )

    action = ActionResult(
        type="send_email_pending",
        details={"to": to, "subject": subject, "status": "pending"},
    )

    return context, [action]


async def handle_confirm_send_email(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Confirm and send the pending email."""
    global _pending_email

    if not _pending_email:
        context = "Nenhum email pendente para enviar."
        return context, []

    email = _pending_email
    _pending_email = None

    result = await send_email(to=email["to"], subject=email["subject"], body=email["body"])

    context = f"Email enviado para {email['to']} com assunto '{email['subject']}'."

    action = ActionResult(
        type="send_email",
        details={
            "to": email["to"],
            "subject": email["subject"],
            "message_id": result["id"],
        },
    )

    logger.info("Email sent to %s: %s", email["to"], result["id"])

    return context, [action]


async def handle_trash_email(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Trash an email by ID, or find and trash emails matching criteria."""
    email_id = intent.parameters.get("email_id", "")

    if not email_id:
        # No specific ID — search for spam/newsletter emails and trash them
        query = intent.parameters.get("query", "is:unread category:promotions OR label:spam")
        emails = await list_emails(query=query, max_results=10)

        if not emails:
            return "Nenhum email de spam/newsletter encontrado para remover.", []

        trashed = []
        for e in emails:
            await trash_email(e["id"])
            trashed.append(e)

        lines = [f"- {e['from']}: {e['subject']}" for e in trashed]
        context = f"Removidos {len(trashed)} emails:\n" + "\n".join(lines)

        action = ActionResult(
            type="trash_email",
            details={"count": len(trashed), "emails": [e["id"] for e in trashed]},
        )
        return context, [action]

    result = await trash_email(email_id)
    context = f"Email removido com sucesso (ID: {email_id})."
    action = ActionResult(type="trash_email", details=result)
    return context, [action]


register_tool(IntentType.READ_EMAIL, handle_read_email)
register_tool(IntentType.SEND_EMAIL, handle_send_email)
register_tool(IntentType.CONFIRM_SEND_EMAIL, handle_confirm_send_email)
register_tool(IntentType.TRASH_EMAIL, handle_trash_email)
