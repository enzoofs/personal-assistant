"""Extract memorable facts from conversations using LLM."""

import json
import logging

from atlas.memory.store import memory_exists, save_memory
from atlas.services.openai_client import chat_completion

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """\
Analise a conversa abaixo e extraia fatos importantes que devem ser lembrados permanentemente.

Tipos de fatos a extrair:
- Preferências do usuário ("prefere X", "gosta de Y", "não gosta de Z")
- Dados pessoais (nome de pessoas, datas importantes, trabalho, projetos)
- Decisões tomadas ("decidiu fazer X", "escolheu Y")
- Padrões observados ("sempre faz X quando Y")
- Contexto relevante ("está trabalhando no projeto X", "tem prova na semana que vem")

NÃO extraia:
- Detalhes triviais de uma única interação
- Informações genéricas que qualquer pessoa saberia
- Comandos operacionais ("cria evento", "mostra agenda")

Retorne um JSON array. Para cada fato:
{
  "content": "frase concisa descrevendo o fato",
  "category": "preference|personal|decision|pattern|context"
}

Se não houver fatos relevantes, retorne [].
Responda APENAS com JSON válido, sem markdown.\
"""


async def extract_memories(conversation: list[dict]) -> list[dict]:
    """Extract memorable facts from a conversation window.

    Args:
        conversation: List of message dicts with role and content.

    Returns:
        List of extracted memory dicts.
    """
    if len(conversation) < 2:
        return []

    conv_text = "\n".join(f"{m['role']}: {m['content']}" for m in conversation)

    try:
        raw = await chat_completion(
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": conv_text},
            ],
            temperature=0.1,
        )
        facts = json.loads(raw)
        if not isinstance(facts, list):
            return []

        saved = []
        for fact in facts:
            content = fact.get("content", "").strip()
            category = fact.get("category", "fact")
            if content and not memory_exists(content):
                save_memory(content=content, category=category)
                saved.append(fact)
                logger.info("Memory saved: [%s] %s", category, content)

        return saved

    except (json.JSONDecodeError, Exception) as e:
        logger.warning("Memory extraction failed: %s", e)
        return []
