# Arquitetura — ATLAS MVP (Fase 1)

## Status: Approved

---

## Visão Geral

ATLAS MVP é um backend Python/FastAPI com endpoint REST (`POST /chat`) que recebe texto do usuário, classifica a intenção via GPT-4o-mini, executa a ação correspondente (notas, calendário, hábitos, pesquisa) e responde com personalidade sarcástica.

### Diagrama

```
┌──────────────────────────────────────────────────────┐
│                    FastAPI Server                      │
│                                                        │
│  POST /chat ──► Orchestrator                           │
│                     │                                  │
│              ┌──────▼──────┐                           │
│              │   Intent     │  ← Chamada 1 ao LLM     │
│              │  Classifier  │                          │
│              └──────┬──────┘                           │
│                     │                                  │
│              ┌──────▼──────┐                           │
│              │   Intent     │                          │
│              │   Router     │                          │
│              └──────┬──────┘                           │
│                     │                                  │
│         ┌───────┬───┴───┬────────┬──────────┐         │
│         ▼       ▼       ▼        ▼          ▼         │
│    Obsidian  Google   Habit   Search    Briefing      │
│    Manager   Cal.     Tracker Engine    Generator     │
│         │       │       │        │          │         │
│         └───────┴───┬───┴────────┴──────────┘         │
│                     │                                  │
│              ┌──────▼──────┐                           │
│              │  Response    │  ← Chamada 2 ao LLM     │
│              │  Generator   │  (+ persona ATLAS)       │
│              └──────┬──────┘                           │
│                     │                                  │
│  ◄──────────────────┘                                  │
└──────────────────────────────────────────────────────┘
         │                    │
    ┌────▼────┐         ┌────▼────┐
    │Obsidian │         │ChromaDB │
    │  Vault  │         │ (local) │
    └─────────┘         └─────────┘
```

## Estrutura do Projeto

```
atlas/
├── pyproject.toml
├── .env.example
├── atlas/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, POST /chat endpoint
│   ├── config.py               # pydantic-settings, carrega .env
│   ├── orchestrator.py         # Fluxo: classify → route → execute → respond
│   ├── intent/
│   │   ├── __init__.py
│   │   ├── classifier.py       # GPT-4o-mini classifica intenção do usuário
│   │   └── schemas.py          # Pydantic models: IntentResult, cada intenção
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── obsidian.py         # CRUD no vault (criar nota, categorizar, daily note)
│   │   ├── calendar.py         # Google Calendar API (CRUD de eventos)
│   │   ├── habits.py           # Parse texto → registro estruturado no vault
│   │   ├── search.py           # ChromaDB (vault) + Tavily (web)
│   │   └── briefing.py         # Agrega calendar + vault + habits → briefing diário
│   ├── persona/
│   │   ├── __init__.py
│   │   └── atlas.py            # System prompt ATLAS + response generation
│   ├── vault/
│   │   ├── __init__.py
│   │   ├── manager.py          # Leitura/escrita de markdown no filesystem
│   │   ├── indexer.py          # ChromaDB indexação incremental (upsert por file hash)
│   │   └── templates.py        # Templates markdown (daily note, habit log, etc.)
│   └── services/
│       ├── __init__.py
│       ├── openai_client.py    # Wrapper OpenAI SDK (chat completions + embeddings)
│       └── google_auth.py      # OAuth2 flow Google Calendar
├── vault/                      # Obsidian vault (gitignored)
│   ├── daily/
│   ├── inbox/
│   ├── projects/
│   ├── people/
│   ├── habits/
│   │   ├── health/
│   │   └── productivity/
│   ├── research/
│   ├── insights/
│   └── templates/
├── chroma_db/                  # ChromaDB persistent (gitignored)
└── tests/
    ├── test_orchestrator.py
    ├── test_classifier.py
    ├── test_obsidian.py
    ├── test_calendar.py
    └── test_habits.py
```

## Fluxo de Request

```
1. POST /chat { "message": "marca reunião com João amanhã às 15h" }
2. Orchestrator recebe mensagem
3. IntentClassifier (GPT-4o-mini) → { intent: "create_event", params: { title: "Reunião com João", datetime: "2026-02-03T15:00" } }
4. Router despacha para CalendarManager.create_event()
5. CalendarManager cria evento via Google Calendar API → retorna confirmação
6. ResponseGenerator (GPT-4o-mini + system prompt ATLAS) → "Reunião com o João marcada pra amanhã às 15h. Tenta não cancelar dessa vez."
7. Retorna resposta ao cliente
```

### Intenções suportadas

| Intent | Tool | Descrição |
|---|---|---|
| `save_note` | ObsidianManager | Criar/atualizar nota no vault |
| `create_event` | CalendarManager | Criar evento no Google Calendar |
| `query_calendar` | CalendarManager | Listar/consultar eventos |
| `log_habit` | HabitTracker | Registrar dado de hábito/saúde |
| `search` | SearchEngine | Busca no vault (ChromaDB) + web (Tavily) |
| `briefing` | BriefingGenerator | Resumo do dia (agenda + tarefas + hábitos) |
| `chat` | (nenhuma) | Conversa casual, direto pro ResponseGenerator |

## Stack e Dependências

```toml
[project]
dependencies = [
    "fastapi>=0.115",
    "uvicorn>=0.34",
    "openai>=1.60",
    "chromadb>=0.6",
    "tavily-python>=0.5",
    "google-api-python-client>=2.160",
    "google-auth-oauthlib>=1.2",
    "pydantic-settings>=2.7",
    "python-frontmatter>=1.1",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "httpx>=0.28",           # TestClient async
]
```

## Decisões de Design

### 1. Classificador separado (2 chamadas LLM)

Em vez de function calling nativo, usamos 2 chamadas:
- **Chamada 1:** classifica intenção + extrai parâmetros
- **Chamada 2:** gera resposta com personalidade

**Justificativa:** mais controle sobre routing, logging e debugging. Cada tool pode ser testada isoladamente.

### 2. Vault no filesystem direto

Backend e vault na mesma máquina. Acesso via `pathlib` + `python-frontmatter`.

**Justificativa:** zero complexidade de sync. Compatível com Obsidian app rodando na mesma máquina.

### 3. ChromaDB com indexação incremental

- Hash SHA256 do conteúdo de cada arquivo como ID
- `upsert()` para add/update automático
- Indexação roda no startup + watcher de filesystem (opcional)

### 4. API REST síncrona

`POST /chat` retorna resposta completa. Streaming (SSE) planejado para Fase 2.

## Riscos e Mitigações

| Risco | Mitigação |
|---|---|
| Latência 3-4s (2 chamadas LLM) | Aceitável pro MVP. Cache de classificações frequentes como futuro |
| Race condition vault (Obsidian + ATLAS) | ATLAS só adiciona/atualiza, nunca deleta. Risco baixo single-user |
| ChromaDB sem backup | Índice é reconstruível a partir do vault. Vault é o source of truth |
| Token de Google Calendar expira | Auto-refresh implementado no google_auth.py |
| Custo API pode crescer | GPT-4o-mini é barato. Monitorar tokens via logging |

## Arquivos Principais a Criar

1. `atlas/main.py` — FastAPI app
2. `atlas/config.py` — Settings
3. `atlas/orchestrator.py` — Core do fluxo
4. `atlas/intent/classifier.py` — Classificação de intenção
5. `atlas/intent/schemas.py` — Modelos de dados
6. `atlas/tools/obsidian.py` — Gestão do vault
7. `atlas/tools/calendar.py` — Google Calendar
8. `atlas/tools/habits.py` — Tracking de hábitos
9. `atlas/tools/search.py` — Busca semântica + web
10. `atlas/tools/briefing.py` — Briefing diário
11. `atlas/persona/atlas.py` — Personalidade
12. `atlas/vault/manager.py` — CRUD markdown
13. `atlas/vault/indexer.py` — ChromaDB indexer
14. `atlas/services/openai_client.py` — OpenAI wrapper
15. `atlas/services/google_auth.py` — OAuth2
