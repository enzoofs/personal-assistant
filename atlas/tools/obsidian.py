import logging
import re
from datetime import datetime

import zoneinfo

from atlas.config import settings
from atlas.intent.schemas import ActionResult, IntentResult, IntentType
from atlas.orchestrator import register_tool
from atlas.vault.manager import append_to_daily_note, write_note
from atlas.vault.templates import note_template
from atlas.vault.topic_extractor import extract_topics

logger = logging.getLogger(__name__)


def slugify(text: str, max_length: int = 50) -> str:
    """Convert text to a slug suitable for filenames.

    Args:
        text: Text to slugify
        max_length: Maximum length of the slug

    Returns:
        Slugified text in kebab-case
    """
    # Take first max_length characters
    text = text[:max_length]

    # Convert to lowercase
    text = text.lower()

    # Replace spaces and special characters with hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)

    # Remove leading/trailing hyphens
    text = text.strip("-")

    return text


async def handle_save_note(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Handle save_note intent.

    Args:
        intent: IntentResult with parameters

    Returns:
        Tuple of (context_string_for_persona, list_of_actions)
    """
    # Extract parameters
    content = intent.parameters.get("content", "")
    category = intent.parameters.get("category", "inbox")
    tags = intent.parameters.get("tags", [])

    if not content:
        raise ValueError("Content is required for saving a note")

    # Generate filename from content
    filename = slugify(content, max_length=50) + ".md"

    # Get title (first line or first ~50 chars of content)
    title_match = re.match(r"^#\s+(.+)", content)
    if title_match:
        title = title_match.group(1).strip()
    else:
        # Use first line or first 50 chars
        first_line = content.split("\n")[0].strip()
        title = first_line[:50] if len(first_line) > 50 else first_line

    # Extract topics via LLM
    topics = await extract_topics(content)

    # Create note using template
    frontmatter_data, template_content = note_template(title, category, tags)
    frontmatter_data["topics"] = list(set(tags + topics))
    frontmatter_data["created_from"] = "chat"

    # Append the actual content if it's not just a title
    if not content.strip().startswith("# "):
        full_content = template_content + content
    else:
        full_content = content

    # Write note to vault with auto-linking
    note_path = f"{category}/{filename}"
    write_note(note_path, frontmatter_data, full_content, auto_link_content=True)

    # Get current time for the reference
    tz = zoneinfo.ZoneInfo(settings.timezone)
    now = datetime.now(tz)
    time_str = now.strftime("%H:%M")

    # Append reference to daily note
    reference_text = f"- [{time_str}] [[{filename[:-3]}]] — {title}"
    append_to_daily_note("## Notas", reference_text)

    # Build context for persona
    context = f"Nota salva em '{category}/{filename}' com título '{title}'. Referência adicionada à nota diária."

    # Build action result
    action = ActionResult(
        type="save_note",
        details={
            "path": note_path,
            "title": title,
            "category": category,
            "tags": tags,
            "filename": filename
        }
    )

    logger.info("Saved note: %s", note_path)

    return context, [action]


# Register the tool
register_tool(IntentType.SAVE_NOTE, handle_save_note)
