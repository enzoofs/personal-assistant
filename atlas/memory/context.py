"""Unified persistent context for ATLAS responses."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from zoneinfo import ZoneInfo

from atlas.config import settings
from atlas.memory.retriever import retrieve_relevant_memories
from atlas.memory.store import get_recent_memories, get_memories_by_category
from atlas.vault.semantic_search import semantic_search
from atlas.vault.manager import read_note, get_daily_note_path, _vault_path

logger = logging.getLogger(__name__)


async def build_context(
    query: str,
    include_vault: bool = True,
    include_memories: bool = True,
    include_recent: bool = True,
    max_vault_notes: int = 3,
    max_memories: int = 5,
) -> dict:
    """Build comprehensive context for a query from all sources.

    Combines:
    - Semantically relevant vault notes
    - Conversation memories
    - Recent activity context

    Args:
        query: User's query.
        include_vault: Search vault notes.
        include_memories: Include conversation memories.
        include_recent: Include recent activity.
        max_vault_notes: Max vault notes to include.
        max_memories: Max memories to include.

    Returns:
        Dict with context data and formatted string.
    """
    context = {
        "vault_notes": [],
        "memories": [],
        "recent_activity": {},
        "user_facts": [],
        "formatted": "",
    }

    # 1. Semantic search across vault and memories
    if include_vault or include_memories:
        try:
            search_results = await semantic_search(
                query,
                n_results=max_vault_notes,
                include_memories=include_memories,
            )
            context["vault_notes"] = search_results.get("notes", [])[:max_vault_notes]
            context["memories"] = search_results.get("memories", [])[:max_memories]
        except Exception as e:
            logger.warning("Context search failed: %s", e)

    # 2. Get user facts from memories
    try:
        user_facts = get_memories_by_category("user_fact", limit=10)
        context["user_facts"] = [m["content"] for m in user_facts]
    except Exception as e:
        logger.warning("Failed to get user facts: %s", e)

    # 3. Recent activity from today's daily note
    if include_recent:
        try:
            daily_path = str(get_daily_note_path())
            fm, content = read_note(daily_path)

            # Extract recent activity
            context["recent_activity"] = {
                "date": fm.get("date", ""),
                "has_events": "## Agenda" in content and len(content.split("## Agenda")[1].split("##")[0].strip()) > 5,
                "has_notes": "## Notas" in content and len(content.split("## Notas")[1].split("##")[0].strip()) > 5,
                "has_habits": "## Hábitos" in content and len(content.split("## Hábitos")[1].split("##")[0].strip()) > 5,
            }
        except FileNotFoundError:
            pass
        except Exception as e:
            logger.warning("Failed to read daily note: %s", e)

    # 4. Format context for LLM
    context["formatted"] = _format_context(context)

    return context


def _format_context(context: dict) -> str:
    """Format context dict into a string for LLM consumption.

    Args:
        context: Context dict from build_context.

    Returns:
        Formatted context string.
    """
    parts = []

    # User facts (important!)
    if context.get("user_facts"):
        parts.append("=== Sobre o Usuário ===")
        for fact in context["user_facts"][:5]:
            parts.append(f"• {fact}")
        parts.append("")

    # Relevant vault notes
    if context.get("vault_notes"):
        parts.append("=== Notas Relevantes ===")
        for note in context["vault_notes"]:
            parts.append(f"📄 [{note['title']}] ({note.get('category', '')})")
            if note.get("snippet"):
                parts.append(f"   {note['snippet'][:200]}...")
        parts.append("")

    # Memories
    if context.get("memories"):
        parts.append("=== Memórias ===")
        for mem in context["memories"]:
            parts.append(f"• [{mem.get('category', '')}] {mem['content']}")
        parts.append("")

    return "\n".join(parts) if parts else ""


async def get_user_profile() -> dict:
    """Get a summary of what ATLAS knows about the user.

    Returns:
        Dict with user information from memories and vault.
    """
    profile = {
        "facts": [],
        "preferences": [],
        "recent_topics": [],
        "people_mentioned": [],
    }

    # User facts
    try:
        facts = get_memories_by_category("user_fact", limit=20)
        profile["facts"] = [m["content"] for m in facts]
    except Exception:
        pass

    # Preferences
    try:
        prefs = get_memories_by_category("user_preference", limit=10)
        profile["preferences"] = [m["content"] for m in prefs]
    except Exception:
        pass

    # Recent topics from memories
    try:
        recent = get_recent_memories(limit=20)
        topics = set()
        for m in recent:
            # Simple topic extraction from memory content
            words = m["content"].lower().split()
            # Skip common words, keep potential topics
            for word in words:
                if len(word) > 4 and word.isalpha():
                    topics.add(word)
        profile["recent_topics"] = list(topics)[:10]
    except Exception:
        pass

    # People mentioned (from people folder in vault)
    try:
        from atlas.vault.manager import list_notes
        people_notes = list_notes("people")
        profile["people_mentioned"] = [p.stem for p in people_notes[:10]]
    except Exception:
        pass

    return profile


async def remember_from_conversation(
    user_message: str,
    assistant_response: str,
    intent: Optional[str] = None,
) -> list[str]:
    """Extract things to remember from a conversation turn.

    Called after each conversation to extract important facts.

    Args:
        user_message: User's message.
        assistant_response: Assistant's response.
        intent: Detected intent if available.

    Returns:
        List of extracted facts to remember.
    """
    from atlas.services.openai_client import chat_completion

    prompt = f"""\
Analise esta conversa e extraia FATOS sobre o usuário que valem lembrar.

Usuário: {user_message}
Assistente: {assistant_response}

Extraia apenas informações factuais e preferências pessoais como:
- Nome, profissão, localização
- Preferências (gosta de X, não gosta de Y)
- Hábitos mencionados
- Pessoas importantes (família, colegas)
- Projetos em andamento

NÃO extraia:
- Comandos operacionais
- Informações genéricas
- Detalhes da conversa em si

Retorne JSON array de strings. Se não houver nada relevante, retorne [].
Exemplo: ["Usuário trabalha com tecnologia", "Prefere café pela manhã"]

Responda APENAS com JSON válido.\
"""

    try:
        response = await chat_completion(
            messages=[
                {"role": "system", "content": "Você extrai fatos sobre usuários de conversas."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        import json
        facts = json.loads(response)

        if not isinstance(facts, list):
            return []

        # Save facts as memories
        from atlas.memory.store import add_memory

        saved = []
        for fact in facts:
            if isinstance(fact, str) and len(fact) > 10:
                add_memory(fact, category="user_fact", confidence=0.8)
                saved.append(fact)
                logger.info("Remembered user fact: %s", fact[:50])

        return saved

    except Exception as e:
        logger.warning("Failed to extract facts from conversation: %s", e)
        return []


def get_conversation_context_prompt(context: dict) -> str:
    """Generate a system prompt addition with context.

    Args:
        context: Context dict from build_context.

    Returns:
        System prompt addition string.
    """
    if not context.get("formatted"):
        return ""

    return f"""
=== CONTEXTO DO USUÁRIO ===
Use estas informações para personalizar sua resposta:

{context['formatted']}

Importante:
- Referencie notas relevantes quando apropriado
- Use fatos conhecidos sobre o usuário para personalizar
- Conecte com memórias anteriores quando fizer sentido
================================
"""
