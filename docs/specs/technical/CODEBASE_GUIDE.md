# Guia de Navegação da Base de Código — ATLAS

## Estrutura de Diretórios

```
personal-assistant/
├── atlas/                    # Backend Python (FastAPI)
│   ├── __init__.py
│   ├── main.py              # Entry point: FastAPI app, endpoints, startup
│   ├── config.py            # Settings singleton (pydantic-settings + .env)
│   ├── orchestrator.py      # Pipeline: classify → route → execute → respond
│   ├── intent/
│   │   ├── classifier.py    # classify_intent() via GPT-4o-mini
│   │   └── schemas.py       # IntentType enum, Pydantic models
│   ├── tools/
│   │   ├── __init__.py      # Auto-import de todos os tools
│   │   ├── obsidian.py      # save_note handler
│   │   ├── calendar.py      # create_event, query_calendar, delete_event
│   │   ├── habits.py        # log_habit handler
│   │   ├── briefing.py      # briefing handler
│   │   └── search.py        # search handler (vault + web)
│   ├── persona/
│   │   └── atlas.py         # SYSTEM_PROMPT (130 linhas) + generate_response()
│   ├── services/
│   │   ├── openai_client.py # OpenAI SDK wrapper (chat, whisper, TTS)
│   │   └── google_calendar.py # Google Calendar OAuth2 + CRUD
│   └── vault/               # [NÃO IMPLEMENTADO]
│       ├── manager.py       # CRUD de notas no filesystem
│       ├── indexer.py       # ChromaDB indexação/busca semântica
│       └── templates.py     # Templates de notas markdown
│
├── mobile/                   # App React Native (Expo)
│   ├── App.tsx              # Root component
│   ├── app.json             # Expo config
│   ├── eas.json             # EAS Build config
│   ├── src/
│   │   ├── api/atlas.ts     # HTTP client (sendChat, sendVoice, checkHealth)
│   │   ├── screens/HomeScreen.tsx  # Tela principal de chat
│   │   ├── components/
│   │   │   ├── MessageBubble.tsx   # Bolha de mensagem animada
│   │   │   ├── ActionCard.tsx      # Card visual para ações executadas
│   │   │   ├── ChatInput.tsx       # Input de texto
│   │   │   ├── MicButton.tsx       # Botão de gravação de voz
│   │   │   └── TypingIndicator.tsx # Indicador "digitando..."
│   │   ├── hooks/
│   │   │   ├── useChat.ts         # Estado do chat e envio de mensagens
│   │   │   └── useAudio.ts        # Gravação e reprodução de áudio
│   │   ├── theme/index.ts         # Design tokens (cores, espaçamento, fontes)
│   │   └── types/index.ts         # TypeScript interfaces
│   └── assets/                    # Ícones e splash screen
│
├── tests/                    # Testes Python (pytest)
│   ├── conftest.py          # Fixtures compartilhadas
│   ├── test_api.py          # Testes de endpoints FastAPI
│   ├── test_orchestrator.py # Testes do pipeline
│   ├── test_tools.py        # Testes dos tool handlers
│   ├── test_schemas.py      # Testes de Pydantic models
│   ├── test_slugify.py      # Testes de slugificação
│   ├── test_vault_manager.py # Testes do vault (implementação pendente)
│   └── test_templates.py    # Testes de templates (implementação pendente)
│
├── docs/                     # Documentação do projeto
├── .github/
│   ├── architecture/        # Documentos de arquitetura
│   └── issues/              # Specs e user stories
├── pyproject.toml           # Dependências Python
├── pytest.ini               # Configuração de testes
└── .env.example             # Template de variáveis de ambiente
```

## Arquivos Chave e Seus Papéis

### Entry Points
| Arquivo | Papel |
|---|---|
| `atlas/main.py` | FastAPI app, define endpoints, startup hook (vault init + indexação) |
| `mobile/App.tsx` | Root do app mobile, navigation setup |

### Fluxo Principal (Backend)
| Arquivo | Papel no Pipeline |
|---|---|
| `atlas/main.py` | Recebe POST /chat → valida API key → chama `process()` |
| `atlas/orchestrator.py` | `process()`: classify → lookup tool → execute → generate_response |
| `atlas/intent/classifier.py` | `classify_intent()`: prompt + GPT-4o-mini → IntentResult JSON |
| `atlas/tools/*.py` | Handlers executam ação concreta → retornam (context, actions) |
| `atlas/persona/atlas.py` | `generate_response()`: context + SYSTEM_PROMPT → resposta final |

### Configuração
| Arquivo | O que configura |
|---|---|
| `atlas/config.py` | Settings singleton: API keys, paths, timezone, modelo LLM |
| `.env` | Valores reais (não commitado) |
| `.env.example` | Template com variáveis necessárias |
| `pyproject.toml` | Dependências Python e metadados |

## Fluxo de Dados

```
[Mobile App]
    │
    │  POST /chat { message: "Marca reunião amanhã 15h" }
    │  Header: X-API-Key
    ▼
[main.py] ─── valida API key
    │
    ▼
[orchestrator.process()]
    │
    ├──► [classifier.classify_intent()]
    │       │
    │       │  GPT-4o-mini call #1
    │       │  Prompt: "Classifique em 8 intents..."
    │       │
    │       ▼
    │    IntentResult { intent: "create_event", params: { title, datetime }, confidence: 0.95 }
    │
    ├──► [tools/calendar.handle_create_event()]
    │       │
    │       │  Google Calendar API
    │       │
    │       ▼
    │    (context: "Evento criado: ...", actions: [{ type: "calendar_event_created", ... }])
    │
    ├──► [persona/atlas.generate_response()]
    │       │
    │       │  GPT-4o-mini call #2
    │       │  System: ATLAS personality prompt
    │       │  User: message + context da ação
    │       │
    │       ▼
    │    "Reunião marcada. Tenta não cancelar dessa vez."
    │
    ▼
[main.py] ─── return ChatResponse { response, intent, actions }
    │
    ▼
[Mobile App] ─── exibe MessageBubble + ActionCard
```

## Pontos de Integração Externa

| Serviço | Arquivo | Criticidade |
|---|---|---|
| OpenAI API | `services/openai_client.py` | Crítica (classificação + resposta) |
| Google Calendar | `services/google_calendar.py` | Alta (agenda) |
| Tavily API | `tools/search.py` | Média (busca web) |
| ChromaDB | `vault/indexer.py` [pendente] | Alta (busca no vault) |
| Obsidian vault | `vault/manager.py` [pendente] | Crítica (storage) |

## Mobile → Backend

O app mobile se conecta ao backend via HTTP:
- **Dev**: via ngrok tunnel (URL hardcoded em `src/api/atlas.ts`)
- **Produção**: via IP público da Oracle Cloud VPS
- **Auth**: header `X-API-Key`
- **Endpoints**: `POST /chat`, `POST /voice`, `GET /health`
