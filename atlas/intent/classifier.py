import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from atlas.config import settings
from atlas.intent.schemas import IntentResult, IntentType
from atlas.services.openai_client import chat_completion

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT_TEMPLATE = """\
Data e hora atual: {now}

Você é um classificador de intenções. Analise a mensagem do usuário e retorne um JSON com:
- "intent": uma das opções abaixo
- "parameters": parâmetros extraídos relevantes para a intenção
- "confidence": confiança de 0.0 a 1.0

Intenções possíveis:
- "save_note": usuário quer salvar/anotar algo. Params: {{"content": "...", "category": "inbox|projects|people|research"}}
- "create_event": usuário quer criar compromisso. Params: {{"title": "...", "datetime": "ISO 8601", "description": "..."}}
- "query_calendar": usuário quer ver agenda. Params: {{"period": "today|tomorrow|week"}}
- "delete_event": usuário quer cancelar/deletar/remover evento. Params: {{"title": "...", "date": "YYYY-MM-DD"}}
- "edit_event": usuário quer editar/alterar/mover/reagendar evento. Params: {{"title": "...", "date": "YYYY-MM-DD", "new_title": "...", "new_datetime": "ISO 8601", "new_description": "..."}}
- "log_habit": usuário registra hábito/saúde. Params: {{"type": "sleep|exercise|mood|custom", "value": "...", "unit": "..."}}
- "read_email": usuário quer ver/ler/checar emails. Params: {{"query": "is:unread|from:...|subject:...", "max_results": 5}}
- "send_email": usuário quer enviar/responder email. Params: {{"to": "email@...", "subject": "...", "body": "..."}}
- "confirm_send_email": usuário confirma o envio de um email previamente preparado (ex: "sim", "pode enviar", "confirma"). Params: {{}}
- "trash_email": usuário quer deletar/remover/limpar email(s) — spam, newsletter indesejada, lixo. Params: {{"email_id": "...", "reason": "spam|newsletter|unwanted"}}
- "search": usuário quer pesquisar algo. Params: {{"query": "...", "source": "vault|web|both"}}
- "briefing": usuário pede resumo do dia. Params: {{}}
- "shopping_add": usuário quer adicionar item à lista de compras (preciso comprar, adiciona na lista, falta...). Params: {{"items": ["item1", "item2"], "category": "mercado|farmácia|limpeza|geral"}}
- "shopping_list": usuário quer ver/listar itens da lista de compras. Params: {{}}
- "shopping_complete": usuário comprou/marcou item como comprado. Params: {{"item": "...", "item_id": number}}
- "chat": conversa casual, sem ação específica. Params: {{}}

IMPORTANTE: Use o histórico da conversa para resolver referências ambíguas. Se o usuário diz \
"cancela esse" ou "deleta", identifique o evento/nota mencionado anteriormente no histórico \
e extraia os parâmetros corretos.

Responda APENAS com JSON válido, sem markdown.\
"""


async def classify_intent(message: str, history: list[dict] | None = None) -> IntentResult:
    try:
        now_str = datetime.now(ZoneInfo(settings.timezone)).strftime("%Y-%m-%d %H:%M")
        messages = [
            {"role": "system", "content": CLASSIFICATION_PROMPT_TEMPLATE.format(now=now_str)},
        ]
        if history:
            messages.extend(history[-10:])
        messages.append({"role": "user", "content": message})
        raw = await chat_completion(
            messages=messages,
            temperature=0.1,
        )
        data = json.loads(raw)
        return IntentResult(
            intent=IntentType(data["intent"]),
            parameters=data.get("parameters", {}),
            confidence=data.get("confidence", 1.0),
        )
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.warning("Falha na classificação, fallback para chat: %s", e)
        return IntentResult(intent=IntentType.CHAT)
