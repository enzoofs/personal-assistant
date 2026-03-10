# Guia de Desenvolvimento com IA — ATLAS

## Contexto Rápido

ATLAS é um assistente pessoal FastAPI que processa linguagem natural via pipeline: classificação de intenção (GPT-4o-mini com fallback Groq) → execução de tool → geração de resposta com personalidade. Storage em markdown (Obsidian vault), busca vetorial via ChromaDB, dados transientes em SQLite.

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
- **Fallbacks** para todos os serviços externos (LLM, TTS, Search)

### Organização de Código
```
atlas/
├── main.py              # FastAPI app + endpoints
├── config.py            # Settings singleton (pydantic-settings)
├── orchestrator.py      # Pipeline: classify → route → execute → respond
├── conversation.py      # Gerenciamento de histórico de sessão
├── errors.py            # Exceções customizadas
├── api/
│   └── dashboard.py     # Endpoint de dashboard agregado
├── intent/
│   ├── classifier.py    # classify_intent() — prompt + parsing
│   └── schemas.py       # IntentType (16), IntentResult, ChatRequest/Response
├── tools/               # Handlers por intenção (auto-registrados)
│   ├── obsidian.py      # save_note
│   ├── calendar.py      # create_event, query_calendar, delete_event, edit_event
│   ├── habits.py        # log_habit
│   ├── briefing.py      # briefing
│   ├── search.py        # search (vault + web com fallback DuckDuckGo)
│   ├── email.py         # read_email, send_email, confirm_send_email, trash_email
│   ├── shopping.py      # shopping_add, shopping_list, shopping_complete
│   └── vault_ops.py     # search_vault, daily_summary, voice_capture, find_connections
├── persona/
│   └── atlas.py         # SYSTEM_PROMPT + generate_response() + streaming
├── services/
│   ├── openai_client.py # chat_completion, transcribe, TTS (multi-tier)
│   ├── google_auth.py   # OAuth2 credential management
│   ├── google_calendar.py # Calendar CRUD
│   └── gmail.py         # Email read/send/trash
├── memory/
│   ├── store.py         # SQLite: sessions, shopping list, memories
│   ├── retriever.py     # Busca de memórias relevantes
│   ├── extractor.py     # Extração de memórias de conversas
│   └── context.py       # Fatos do usuário para contexto
├── vault/
│   ├── manager.py       # CRUD de notas + daily notes
│   ├── indexer.py       # ChromaDB indexação/busca
│   ├── templates.py     # Templates de notas
│   ├── semantic_search.py # Busca semântica com contexto
│   ├── connections.py   # Backlinks, orphans, graph
│   ├── daily_summary.py # Geração de resumo diário
│   ├── voice_capture.py # Transcrição → nota estruturada
│   ├── knowledge_extractor.py # Extração de conhecimento
│   ├── linker.py        # Auto-linking entre notas
│   ├── topic_extractor.py # Extração de tópicos
│   └── stats.py         # Estatísticas do vault
└── proactive/
    └── email_cleaner.py # Triagem automática de email em background
```

## Como Adicionar um Novo Tool

1. Criar arquivo em `atlas/tools/novo_tool.py`
2. Importar e usar `register_tool` do orchestrator
3. Definir handler async que retorna `(context: str, actions: list[ActionResult])`
4. O registro acontece no import — o `tools/__init__.py` auto-importa tudo
5. Adicionar o intent em `IntentType` enum e no prompt de classificação em `classifier.py`

```python
from atlas.orchestrator import register_tool
from atlas.intent.schemas import IntentType, IntentResult, ActionResult

async def handle_meu_intent(intent: IntentResult) -> tuple[str, list[ActionResult]]:
    params = intent.parameters
    # executar ação
    context = "Resultado para o persona usar na resposta"
    actions = [ActionResult(type="minha_acao", details={"key": "value"})]
    return context, actions

register_tool(IntentType.MEU_INTENT, handle_meu_intent)
```

## Como Funciona o Pipeline

### Fluxo Normal (`POST /chat`)
```
1. POST /chat { message: "...", session_id: "..." }
2. Paralelo: classify_intent() + retrieve_memories() + get_vault_context()
3. orchestrator busca handler registrado para o intent
4. handler executa ação (vault, calendar, email, etc.) → (context, actions)
5. generate_response(message, intent, context, memories, vault_context)
6. Background: extract_memories(), extract_knowledge(), remember_from_conversation()
7. Return ChatResponse { response, intent, actions, error }
```

### Fluxo Streaming (`POST /chat/stream`)
```
1. POST /chat/stream { message: "...", session_id: "..." }
2. Mesmo pipeline até passo 4
3. generate_response_stream() → yield tokens via SSE
4. data: {"type": "token", "content": "..."}\n\n
5. data: {"type": "done", "intent": "...", "actions": [...]}\n\n
```

## Sistema de Fallbacks

| Serviço | Principal | Fallback (gratuito) |
|---|---|---|
| LLM (chat/classificação) | OpenAI GPT-4o-mini | Groq Llama 3.1 8B |
| TTS | ElevenLabs → OpenAI | Edge TTS (Microsoft) |
| Busca Web | Tavily | DuckDuckGo |

Configuração via `.env`:
```
GROQ_API_KEY=gsk_...
EDGE_TTS_VOICE=pt-BR-AntonioNeural
RESPONSE_MODE=text|audio|audio_premium
```

## Pegadinhas e Armadilhas

### Auto-registro de tools
O `tools/__init__.py` importa todos os módulos da pasta. Se um módulo falhar no import (ex: dependência faltando), todos os tools falham silenciosamente.

### Timezone
Todas as operações de data/hora usam a timezone configurada em `TIMEZONE` (.env). O classifier injeta data/hora atual no prompt para resolução temporal correta.

### ChromaDB no startup
`index_vault()` roda no startup do FastAPI. Se o vault for grande, o startup pode ser lento.

### Google OAuth
Primeiro uso requer interação do navegador para consentimento OAuth. Em servidor headless (Oracle Cloud), copiar `token.json` manualmente.

### Respostas sem markdown/URLs
As respostas do ATLAS não devem conter links, URLs ou markdown complexo — precisam ser compatíveis com TTS.

### SQLite para dados transientes
Shopping list, sessões de conversa, e memórias ficam em `memory.db`. Notas ficam em markdown no vault.

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

## Performance

- **Latência típica**: ~2-3s para resposta completa (2 chamadas LLM paralelas quando possível)
- **TTFB com streaming**: ~500ms (tokens começam a chegar)
- **Gargalo**: Classificação LLM (primeira chamada)
- **Otimização implementada**: Streaming SSE, paralelização de tasks, cache de embeddings
