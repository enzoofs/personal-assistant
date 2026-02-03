"""Gmail API service — read and send emails."""

import base64
import logging
from email.mime.text import MIMEText

from googleapiclient.discovery import build

from atlas.services.google_auth import get_credentials

logger = logging.getLogger(__name__)


def _get_service():
    """Build Gmail API service."""
    return build("gmail", "v1", credentials=get_credentials())


async def list_emails(query: str = "", max_results: int = 10) -> list[dict]:
    """List emails matching a query.

    Args:
        query: Gmail search query (e.g. "is:unread", "from:someone@example.com").
        max_results: Maximum number of emails to return.

    Returns:
        List of dicts with id, subject, from, date, snippet.
    """
    service = _get_service()

    result = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    messages = result.get("messages", [])
    if not messages:
        return []

    emails = []
    for msg_ref in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_ref["id"], format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        emails.append({
            "id": msg["id"],
            "subject": headers.get("Subject", "(sem assunto)"),
            "from": headers.get("From", ""),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        })

    return emails


async def get_email(email_id: str) -> dict:
    """Get full email content by ID.

    Args:
        email_id: Gmail message ID.

    Returns:
        Dict with id, subject, from, date, body.
    """
    service = _get_service()

    msg = service.users().messages().get(
        userId="me", id=email_id, format="full"
    ).execute()

    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

    body = _extract_body(msg.get("payload", {}))

    return {
        "id": msg["id"],
        "subject": headers.get("Subject", "(sem assunto)"),
        "from": headers.get("From", ""),
        "date": headers.get("Date", ""),
        "body": body[:3000],
    }


def _extract_body(payload: dict) -> str:
    """Extract plain text body from Gmail payload."""
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    for part in payload.get("parts", []):
        result = _extract_body(part)
        if result:
            return result

    return ""


async def send_email(to: str, subject: str, body: str) -> dict:
    """Send an email.

    Args:
        to: Recipient email address.
        subject: Email subject.
        body: Email body (plain text).

    Returns:
        Dict with id and thread_id.
    """
    service = _get_service()

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    sent = service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()

    logger.info("Email sent to %s: %s", to, sent["id"])

    return {
        "id": sent["id"],
        "thread_id": sent.get("threadId", ""),
    }


async def trash_email(email_id: str) -> dict:
    """Move an email to trash.

    Args:
        email_id: Gmail message ID.

    Returns:
        Dict with id and status.
    """
    service = _get_service()
    service.users().messages().trash(userId="me", id=email_id).execute()
    logger.info("Email trashed: %s", email_id)
    return {"id": email_id, "status": "trashed"}
