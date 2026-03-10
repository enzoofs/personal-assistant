import asyncio
import json
import logging
from typing import AsyncIterator

from atlas.conversation import add_message, get_history, get_message_count
from atlas.intent.classifier import classify_intent
from atlas.intent.schemas import ActionResult, IntentType
from atlas.memory.extractor import extract_memories
from atlas.memory.retriever import retrieve_relevant_memories
from atlas.vault.knowledge_extractor import extract_knowledge
from atlas.persona.atlas import generate_response, generate_response_stream
from atlas.vault.semantic_search import get_context_for_query
from atlas.memory.context import remember_from_conversation

logger = logging.getLogger(__name__)

_tool_registry: dict = {}
_MEMORY_EXTRACTION_INTERVAL = 5
_FACT_EXTRACTION_INTERVAL = 3  # Extract facts more frequently


def register_tool(intent: IntentType, handler):
    _tool_registry[intent] = handler


async def process(message: str, session_id: str = "default") -> tuple[str, str, list[ActionResult], str | None]:
    """Processa uma mensagem do usuário com contexto conversacional."""
    history = get_history(session_id=session_id)

    # Run classification, memory retrieval, and vault context in parallel for speed
    intent_task = classify_intent(message, history=history)
    memories_task = retrieve_relevant_memories(message, k=5)
    vault_context_task = get_context_for_query(message)

    intent_result, memories, vault_context = await asyncio.gather(
        intent_task, memories_task, vault_context_task
    )
    logger.info("Intent: %s (confidence: %.2f)", intent_result.intent.value, intent_result.confidence)

    tool_context = None
    actions: list[ActionResult] = []
    error = None

    handler = _tool_registry.get(intent_result.intent)
    if handler:
        try:
            tool_context, actions = await handler(intent_result)
        except Exception as e:
            logger.exception("Erro ao executar tool %s", intent_result.intent.value)
            error = str(e)

    response = await generate_response(
        message, intent_result, tool_context,
        history=history, memories=memories, vault_context=vault_context,
    )

    add_message("user", message, session_id=session_id)
    add_message("assistant", response, session_id=session_id)

    # Background: extract memories and knowledge every N messages
    msg_count = get_message_count(session_id=session_id)
    if msg_count > 0 and msg_count % _MEMORY_EXTRACTION_INTERVAL == 0:
        full_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response},
        ]
        asyncio.create_task(_extract_memories_background(full_history))
        asyncio.create_task(_extract_knowledge_background(full_history))

    # Extract facts from conversation more frequently
    if msg_count > 0 and msg_count % _FACT_EXTRACTION_INTERVAL == 0:
        asyncio.create_task(_extract_facts_background(message, response, intent_result.intent.value))

    return response, intent_result.intent.value, actions, error


async def process_stream(message: str, session_id: str = "default") -> AsyncIterator[str]:
    """Process message and stream response tokens via Server-Sent Events."""
    history = get_history(session_id=session_id)

    # Run classification, memory retrieval, and vault context in parallel
    intent_task = classify_intent(message, history=history)
    memories_task = retrieve_relevant_memories(message, k=5)
    vault_context_task = get_context_for_query(message)

    intent_result, memories, vault_context = await asyncio.gather(
        intent_task, memories_task, vault_context_task
    )
    logger.info("Intent: %s (confidence: %.2f)", intent_result.intent.value, intent_result.confidence)

    tool_context = None
    actions: list[ActionResult] = []
    error = None

    handler = _tool_registry.get(intent_result.intent)
    if handler:
        try:
            tool_context, actions = await handler(intent_result)
        except Exception as e:
            logger.exception("Erro ao executar tool %s", intent_result.intent.value)
            error = str(e)

    # Stream response tokens
    full_response = []
    async for token in generate_response_stream(
        message, intent_result, tool_context,
        history=history, memories=memories, vault_context=vault_context,
    ):
        full_response.append(token)
        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

    response = "".join(full_response)

    # Send final metadata
    yield f"data: {json.dumps({'type': 'done', 'intent': intent_result.intent.value, 'actions': [a.model_dump() for a in actions], 'error': error})}\n\n"

    # Save to conversation history
    add_message("user", message, session_id=session_id)
    add_message("assistant", response, session_id=session_id)

    # Background memory extraction
    msg_count = get_message_count(session_id=session_id)
    if msg_count > 0 and msg_count % _MEMORY_EXTRACTION_INTERVAL == 0:
        full_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response},
        ]
        asyncio.create_task(_extract_memories_background(full_history))
        asyncio.create_task(_extract_knowledge_background(full_history))

    # Extract facts from conversation more frequently
    if msg_count > 0 and msg_count % _FACT_EXTRACTION_INTERVAL == 0:
        asyncio.create_task(_extract_facts_background(message, response, intent_result.intent.value))


async def _extract_memories_background(history: list[dict]) -> None:
    try:
        recent = history[-10:]
        extracted = await extract_memories(recent)
        if extracted:
            logger.info("Extracted %d memories from conversation", len(extracted))
    except Exception:
        logger.exception("Background memory extraction failed")


async def _extract_knowledge_background(history: list[dict]) -> None:
    try:
        results = await extract_knowledge(history)
        if results:
            logger.info("Extracted %d knowledge notes from conversation", len(results))
    except Exception:
        logger.exception("Background knowledge extraction failed")


async def _extract_facts_background(user_message: str, assistant_response: str, intent: str) -> None:
    """Extract user facts from conversation for persistent context."""
    try:
        facts = await remember_from_conversation(user_message, assistant_response, intent)
        if facts:
            logger.info("Extracted %d user facts from conversation", len(facts))
    except Exception:
        logger.exception("Background fact extraction failed")
