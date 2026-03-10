"""Vault operation handlers for ATLAS intents."""

import logging
from datetime import datetime

from zoneinfo import ZoneInfo

from atlas.config import settings
from atlas.intent.schemas import ActionResult, IntentResult, IntentType
from atlas.orchestrator import register_tool
from atlas.vault.semantic_search import semantic_search, get_context_for_query
from atlas.vault.daily_summary import generate_daily_summary, update_daily_note_with_summary
from atlas.vault.voice_capture import process_voice_capture, quick_capture
from atlas.vault.connections import suggest_connections, get_backlinks, find_orphan_notes

logger = logging.getLogger(__name__)


async def handle_search_vault(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Handle search_vault intent - semantic search in vault.

    Args:
        intent: IntentResult with parameters (query)

    Returns:
        Tuple of (context_string, actions)
    """
    query = intent.parameters.get("query", "")

    if not query:
        raise ValueError("Query é obrigatório para busca no vault")

    results = await semantic_search(query, n_results=5, include_memories=True)

    # Build context for persona
    context_parts = []

    if results["notes"]:
        context_parts.append(f"Encontrei {len(results['notes'])} notas relevantes:")
        for note in results["notes"]:
            context_parts.append(f"- [{note['title']}] ({note['category']}): {note['snippet'][:150]}...")
    else:
        context_parts.append("Não encontrei notas relacionadas no vault.")

    if results["memories"]:
        context_parts.append(f"\nTambém encontrei {len(results['memories'])} memórias relacionadas.")

    context = "\n".join(context_parts)

    action = ActionResult(
        type="search_vault",
        details={
            "query": query,
            "notes_found": len(results["notes"]),
            "memories_found": len(results["memories"]),
            "notes": [{"title": n["title"], "path": n["path"]} for n in results["notes"]],
        }
    )

    logger.info("Vault search: %s -> %d notes, %d memories",
                query[:50], len(results["notes"]), len(results["memories"]))

    return context, [action]


async def handle_daily_summary(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Handle daily_summary intent - generate daily briefing.

    Args:
        intent: IntentResult with optional parameters (date)

    Returns:
        Tuple of (context_string, actions)
    """
    date_str = intent.parameters.get("date")

    if date_str:
        try:
            tz = ZoneInfo(settings.timezone)
            target_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=tz)
        except ValueError:
            target_date = None
    else:
        target_date = None

    # Generate summary
    summary = await generate_daily_summary(target_date)

    # Optionally update the daily note
    if intent.parameters.get("update_daily_note", False):
        path = await update_daily_note_with_summary()
        context = f"Resumo gerado e salvo em {path}:\n\n{summary}"
    else:
        context = f"Resumo do dia:\n\n{summary}"

    action = ActionResult(
        type="daily_summary",
        details={
            "date": date_str or datetime.now().strftime("%Y-%m-%d"),
            "summary_length": len(summary),
        }
    )

    logger.info("Generated daily summary")

    return context, [action]


async def handle_voice_capture(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Handle voice_capture intent - structure voice transcription into note.

    Args:
        intent: IntentResult with parameters (transcription, quick)

    Returns:
        Tuple of (context_string, actions)
    """
    transcription = intent.parameters.get("transcription", "")
    is_quick = intent.parameters.get("quick", False)

    if not transcription:
        raise ValueError("Transcrição é obrigatória")

    if is_quick or len(transcription) < 50:
        result = await quick_capture(transcription)
    else:
        result = await process_voice_capture(transcription)

    context = f"Nota criada: '{result['title']}' em {result['category']}/{result['path'].split('/')[-1]}"

    if result.get("action_items"):
        context += f"\n\nAções identificadas: {len(result['action_items'])}"
        for item in result["action_items"]:
            context += f"\n- {item}"

    if result.get("related"):
        context += f"\n\nNotas relacionadas: {', '.join(result['related'])}"

    action = ActionResult(
        type="voice_capture",
        details={
            "path": result["path"],
            "title": result["title"],
            "category": result["category"],
            "has_actions": bool(result.get("action_items")),
        }
    )

    logger.info("Voice capture saved: %s", result["path"])

    return context, [action]


async def handle_find_connections(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    """Handle find_connections intent - suggest connections for a note.

    Args:
        intent: IntentResult with parameters (note_path or query)

    Returns:
        Tuple of (context_string, actions)
    """
    note_path = intent.parameters.get("note_path", "")
    query = intent.parameters.get("query", "")
    action_type = intent.parameters.get("action", "suggest")  # suggest, backlinks, orphans

    if action_type == "orphans":
        orphans = find_orphan_notes()
        context = f"Encontrei {len(orphans)} notas órfãs (sem conexões):"
        for o in orphans[:10]:
            context += f"\n- [{o['title']}] ({o['category']})"

        action = ActionResult(
            type="find_orphans",
            details={"count": len(orphans), "orphans": [o["title"] for o in orphans[:10]]},
        )
        return context, [action]

    if action_type == "backlinks" and note_path:
        backlinks = get_backlinks(note_path)
        if backlinks:
            context = f"Notas que referenciam '{note_path}':"
            for bl in backlinks:
                context += f"\n- [[{bl['title']}]]"
        else:
            context = f"Nenhuma nota referencia '{note_path}'."

        action = ActionResult(
            type="backlinks",
            details={"note_path": note_path, "count": len(backlinks)},
        )
        return context, [action]

    # Default: suggest connections
    if not note_path and query:
        # Search for a note first
        from atlas.vault.indexer import search_vault
        results = search_vault(query, n_results=1)
        if results:
            note_path = results[0]["path"]
        else:
            return "Não encontrei a nota especificada.", []

    if not note_path:
        raise ValueError("Especifique uma nota para encontrar conexões")

    suggestions = await suggest_connections(note_path, max_suggestions=5)

    if suggestions:
        context = f"Sugestões de conexão para '{note_path}':"
        for s in suggestions:
            context += f"\n- [[{s['target_title']}]] ({s['strength']}): {s['reason']}"
    else:
        context = "Não encontrei conexões relevantes para sugerir."

    action = ActionResult(
        type="suggest_connections",
        details={
            "note_path": note_path,
            "suggestions": [s["target_title"] for s in suggestions],
        }
    )

    logger.info("Found %d connection suggestions for %s", len(suggestions), note_path)

    return context, [action]


# Register all handlers
register_tool(IntentType.SEARCH_VAULT, handle_search_vault)
register_tool(IntentType.DAILY_SUMMARY, handle_daily_summary)
register_tool(IntentType.VOICE_CAPTURE, handle_voice_capture)
register_tool(IntentType.FIND_CONNECTIONS, handle_find_connections)
