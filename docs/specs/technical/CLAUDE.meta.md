# Guia de Desenvolvimento com IA — ATLAS

## Contexto Rápido

ATLAS é um assistente pessoal FastAPI que processa linguagem natural via pipeline: classificação de intenção (GPT-4o-mini) → execução de tool → geração de resposta com personalidade. Storage em markdown (Obsidian vault), busca vetorial via ChromaDB.

## Convenções de Código

### Nomenclatura
- Arquivos: `snake_case.py`
- Classes: `PascalCase`
- Funções/variáveis: `snake_case`
- Constantes: `UPPER_SNAKE_CASE`
- Arquivos markdown no vault: `kebab-case.md` ou `YYYY-MM-DD.md` (daily notes)

### Padrões Obrigatórios
- **Async/await** em todas as funções de I/O (tools, services, handlers)
- **Pydantic models** para todos os schemas de entrada/saída
- **Type hints** em todas as funções
- **Configuração** via `pydantic-settings` lendo `.env` (nunca hardcode)
- **Frontmatter YAML** obrigatório em toda nota criada pelo ATLAS (`date`, `tags`, `category`)

### Organização de Código
```
atlas/
├── main.py              # FastAPI app + endpoints (não lógica de negócio)
├── config.py            # Settings singleton (pydantic-settings)
├── orchestrator.py      # Pipeline: classify → route → execute → respond
├── intent/              # Classificação de intenção (LLM)
│   ├── classifier.py    # classify_intent() — prompt + parsing
│   └── schemas.py       # IntentType, IntentResult, ChatRequest, ChatResponse
├── tools/               # Handlers por intenção (auto-registrados)
│   ├── __init__.py      # Auto-import de todos os tools
│   ├── obsidian.py      # save_note
│   ├── calendar.py      # create_event, query_calendar, delete_event
│   ├── habits.py        # log_habit
│   ├── briefing.py      # briefing
│   └── search.py        # search (vault + web)
├── persona/             # Geração de resposta com personalidade
│   └── atlas.py         # SYSTEM_PROMPT + generate_response()
├── services/            # Clientes de API externa
│   ├── openai_client.py # chat_completion, transcribe_audio, text_to_speech
│   └── google_calendar.py # OAuth2 + CRUD de eventos
└── vault/               # [A IMPLEMENTAR] Abstração do filesystem
    ├── manager.py       # CRUD de notas + daily notes
    ├── indexer.py       # ChromaDB indexação/busca
    └── templates.py     # Templates de notas
```

## Como Adicionar um Novo Tool

1. Criar arquivo em `atlas/tools/novo_tool.py`
2. Importar e usar `register_tool` do orchestrator
3. Definir handler async que retorna `(context: str, actions: list[ActionResult])`
4. O registro acontece no import — o `tools/__init__.py` auto-importa tudo

```python
from atlas.orchestrator import register_tool
from atlas.intent.schemas import IntentType, ActionResult

async def handle_meu_intent(params: dict) -> tuple[str, list[ActionResult]]:
    # executar ação
    context = "Resultado para o persona usar na resposta"
    actions = [ActionResult(type="minha_acao", details={"key": "value"})]
    return context, actions

register_tool(IntentType.MEU_INTENT, handle_meu_intent)
```

4. Adicionar o intent em `IntentType` enum e no prompt de classificação em `classifier.py`

## Como Funciona o Pipeline

```
1. POST /chat { message: "..." }
2. classify_intent(message) → IntentResult { intent, params, confidence }
3. orchestrator busca handler registrado para o intent
4. handler executa ação (vault, calendar, etc.) → (context, actions)
5. generate_response(message, intent, context) → resposta com personalidade
6. Return ChatResponse { response, intent, actions }
```

## Pegadinhas e Armadilhas

### Módulos vault/ não existem ainda
Os imports `from atlas.vault.manager import ...` vão falhar. Os testes mockam esses módulos. Implementar vault/manager.py, vault/indexer.py e vault/templates.py é prioridade.

### Auto-registro de tools
O `tools/__init__.py` importa todos os módulos da pasta. Se um módulo falhar no import (ex: dependência faltando), todos os tools falham silenciosamente.

### Timezone
Todas as operações de data/hora usam a timezone configurada em `TIMEZONE` (.env). O classifier injeta data/hora atual no prompt para resolução temporal correta.

### ChromaDB no startup
`index_vault()` roda no startup do FastAPI. Se o vault for grande, o startup pode ser lento. Considerar lazy loading ou background task.

### Google Calendar OAuth
Primeiro uso requer interação do navegador para consentimento OAuth. Em servidor headless (Oracle Cloud), usar fluxo offline ou copiar `token.json` manualmente.

### Respostas sem markdown/URLs
As respostas do ATLAS não devem conter links, URLs ou markdown complexo — precisam ser compatíveis com TTS (text-to-speech).

## Testes

### Executar
```bash
pytest                    # todos os testes
pytest -m unit            # só unitários
pytest -m api             # só API
pytest tests/test_tools.py  # arquivo específico
```

### Padrões de Teste
- Mocks para todas as APIs externas (OpenAI, Google, Tavily, ChromaDB)
- Fixtures compartilhadas em `conftest.py` (tmp_vault, mock_settings, etc.)
- `httpx.AsyncClient` para testes de endpoint
- `pytest-asyncio` com mode=auto

### Cobertura atual
- 152+ testes escritos
- Cobertura de schemas, orchestrator, tools, API
- Módulos vault/ têm testes escritos mas implementação pendente

## Performance

- **Latência típica**: ~2-4s por request (2 chamadas LLM)
- **Gargalo**: chamadas sequenciais ao OpenAI
- **Otimização futura**: streaming, caching de classificação, function calling
