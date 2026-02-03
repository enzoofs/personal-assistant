import logging

import time
from collections import defaultdict

from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, Response, StreamingResponse

import atlas.tools.briefing  # noqa: F401 — registers briefing tool
import atlas.tools.calendar  # noqa: F401 — registers calendar tools
import atlas.tools.habits  # noqa: F401 — registers log_habit tool
import atlas.tools.email  # noqa: F401 — registers email tools
import atlas.tools.obsidian  # noqa: F401 — registers save_note tool
import atlas.tools.search  # noqa: F401 — registers search tool
import atlas.tools.shopping  # noqa: F401 — registers shopping list tools
from atlas.config import settings
from atlas.intent.schemas import ChatRequest, ChatResponse
from atlas.orchestrator import process, process_stream
from atlas.services.openai_client import text_to_speech, transcribe_audio
from atlas.vault.indexer import index_vault
from atlas.vault.manager import ensure_vault_structure
from atlas.api.dashboard import get_dashboard_data
from atlas.vault.stats import get_vault_stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

app = FastAPI(title="ATLAS", version="0.1.0", description="Assistente Pessoal com Personalidade")


@app.on_event("startup")
async def startup_event():
    """Initialize vault structure on startup."""
    import asyncio
    from atlas.proactive.email_cleaner import start_email_triage
    from atlas.memory.store import cleanup_expired_sessions

    ensure_vault_structure()
    index_vault()
    asyncio.create_task(start_email_triage())
    asyncio.create_task(_session_cleanup_loop())


async def _session_cleanup_loop():
    """Background task to clean up expired sessions every hour."""
    import asyncio
    from atlas.memory.store import cleanup_expired_sessions

    while True:
        try:
            cleanup_expired_sessions(settings.session_expiry_hours)
        except Exception as e:
            logging.error("Session cleanup failed: %s", e)
        await asyncio.sleep(3600)  # Run every hour


_rate_limit: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_REQUESTS = 30
_RATE_LIMIT_WINDOW = 60  # seconds


async def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if api_key != settings.atlas_api_key:
        raise HTTPException(status_code=401, detail="API key inválida ou ausente")

    # Rate limiting by client IP
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    _rate_limit[client_ip] = [t for t in _rate_limit[client_ip] if now - t < _RATE_LIMIT_WINDOW]
    if len(_rate_limit[client_ip]) >= _RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit excedido. Tente novamente em breve.")
    _rate_limit[client_ip].append(now)


@app.get("/health")
async def health():
    status = {"status": "ok", "version": "0.1.0", "services": {}}
    # Check Google OAuth token
    try:
        from atlas.services.google_auth import get_credentials
        creds = get_credentials()
        status["services"]["google"] = "ok" if creds and creds.valid else "expired"
    except Exception:
        status["services"]["google"] = "error"
    # Check Tavily
    status["services"]["tavily"] = "ok" if settings.tavily_api_key and settings.tavily_api_key != "tvly-test" else "not_configured"
    return status


@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
async def chat(body: ChatRequest):
    response_text, intent, actions, error = await process(body.message, session_id=body.session_id)
    return JSONResponse(
        content=ChatResponse(
            response=response_text,
            intent=intent,
            actions=actions,
            error=error,
        ).model_dump(),
        media_type="application/json; charset=utf-8",
    )


@app.post("/chat/stream", dependencies=[Depends(verify_api_key)])
async def chat_stream(body: ChatRequest):
    """Stream chat response via Server-Sent Events."""
    return StreamingResponse(
        process_stream(body.message, session_id=body.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/vault/stats", dependencies=[Depends(verify_api_key)])
async def vault_stats():
    return get_vault_stats()


@app.get("/dashboard", dependencies=[Depends(verify_api_key)])
async def dashboard():
    return await get_dashboard_data()


@app.delete("/email-alerts", dependencies=[Depends(verify_api_key)])
async def dismiss_email_alerts():
    from atlas.proactive.email_cleaner import clear_email_alerts
    clear_email_alerts()
    return {"status": "cleared"}


@app.post("/voice", dependencies=[Depends(verify_api_key)])
async def voice(file: UploadFile):
    """Receive audio, transcribe, process, and return audio response."""
    audio_bytes = await file.read()
    transcript = await transcribe_audio(audio_bytes, file.filename or "audio.webm")

    response_text, intent, actions, error = await process(transcript)

    tts_bytes = await text_to_speech(response_text)

    return JSONResponse(
        content={
            "transcript": transcript,
            "response": response_text,
            "intent": intent,
            "actions": [a.model_dump() for a in actions],
            "error": error,
            "audio_base64": __import__("base64").b64encode(tts_bytes).decode(),
        },
        media_type="application/json; charset=utf-8",
    )


# --- Shopping List API ---

@app.get("/shopping", dependencies=[Depends(verify_api_key)])
async def get_shopping():
    """Get shopping list items."""
    from atlas.memory.store import get_shopping_list
    items = get_shopping_list(include_completed=False)
    return {"items": items, "count": len(items)}


@app.post("/shopping", dependencies=[Depends(verify_api_key)])
async def add_shopping(body: dict):
    """Add item to shopping list."""
    from atlas.memory.store import add_shopping_item
    item = body.get("item", "").strip()
    if not item:
        raise HTTPException(status_code=400, detail="Item is required")
    quantity = body.get("quantity")
    category = body.get("category", "geral")
    item_id = add_shopping_item(item, quantity=quantity, category=category)
    return {"id": item_id, "item": item, "category": category}


@app.patch("/shopping/{item_id}", dependencies=[Depends(verify_api_key)])
async def update_shopping_item(item_id: int, body: dict):
    """Mark item as completed or uncompleted."""
    from atlas.memory.store import complete_shopping_item, uncomplete_shopping_item
    completed = body.get("completed", True)
    if completed:
        success = complete_shopping_item(item_id)
    else:
        success = uncomplete_shopping_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item_id, "completed": completed}


@app.delete("/shopping/{item_id}", dependencies=[Depends(verify_api_key)])
async def delete_shopping(item_id: int):
    """Delete item from shopping list."""
    from atlas.memory.store import delete_shopping_item
    success = delete_shopping_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "deleted", "id": item_id}


@app.delete("/shopping", dependencies=[Depends(verify_api_key)])
async def clear_completed():
    """Clear all completed items."""
    from atlas.memory.store import clear_completed_shopping
    count = clear_completed_shopping()
    return {"status": "cleared", "count": count}
