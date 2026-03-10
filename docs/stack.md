# Stack Tecnológica

## Linguagem e Runtime

- **Python 3.12+** — Ecossistema AI maduro, tipagem robusta, async nativo

## Framework Principal

- **FastAPI** (`>=0.115`) — API REST async, validação automática via Pydantic, docs OpenAPI grátis

## LLM e AI

| Componente | Tecnologia | Fallback |
|---|---|---|
| Chat/Raciocinio | OpenAI GPT-4o-mini | Groq Llama 3.1 (gratuito) |
| Embeddings | OpenAI text-embedding-3-small | — |
| STT | OpenAI Whisper | — |
| TTS Premium | ElevenLabs | OpenAI TTS -> Edge TTS |
| TTS Gratuito | Edge TTS | — |
| Busca vetorial | ChromaDB (`>=0.6`, local) | — |
| Busca web | Tavily API | DuckDuckGo (gratuito) |

## Storage

- **Obsidian vault** (markdown no filesystem) — Source of truth de todas as notas
- **ChromaDB** (persistente, local) — Índice vetorial reconstruível a partir do vault
- Sem banco de dados relacional — dados vivem como markdown com frontmatter YAML

## Integracoes Externas

- **Google Calendar API** — OAuth2, CRUD de eventos
- **Gmail API** — OAuth2, leitura/envio/triagem de emails
- **OpenAI API** — Chat completions, embeddings, Whisper STT, TTS
- **ElevenLabs API** — TTS premium (opcional)
- **Groq API** — LLM fallback gratuito (opcional)
- **Tavily API** — Busca web (opcional, fallback: DuckDuckGo)

## Dependencias Python

```toml
[project]
dependencies = [
    # Framework
    "fastapi>=0.115",
    "uvicorn>=0.34",
    "sse-starlette>=2.0",        # Server-Sent Events

    # AI/LLM
    "openai>=1.60",
    "groq>=0.5",                  # Fallback LLM (gratuito)
    "chromadb>=0.6",

    # TTS
    "edge-tts>=6.1",              # TTS gratuito
    "httpx>=0.28",                # ElevenLabs API calls

    # Search
    "tavily-python>=0.5",
    "duckduckgo-search>=6.0",     # Fallback (gratuito)

    # Google APIs
    "google-api-python-client>=2.160",
    "google-auth-oauthlib>=1.2",

    # Utils
    "pydantic-settings>=2.7",
    "python-frontmatter>=1.1",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "httpx>=0.28",
]
```

## Mobile App

- **React Native** + **Expo** (SDK 54) — App Android de chat com ATLAS
- **TypeScript** 5.9 / **React** 19.1
- **Expo AV** — Gravação e reprodução de áudio
- **EAS Build** — Build de APK Android para distribuição

### Dependências Mobile Principais

| Biblioteca | Uso |
|---|---|
| `expo-av` | Gravação de voz + reprodução de TTS |
| `expo-file-system` | Acesso a arquivos de áudio |
| `@expo/vector-icons` | Ícones na interface |

### Estrutura Mobile

```
mobile/src/
├── api/atlas.ts         # Cliente HTTP (sendChat, sendVoice, checkHealth)
├── screens/HomeScreen.tsx  # Tela principal de chat
├── components/          # MessageBubble, ActionCard, ChatInput, MicButton, TypingIndicator
├── hooks/               # useChat (estado), useAudio (gravação)
├── theme/index.ts       # Design tokens (cores, espaçamento, fontes)
└── types/index.ts       # TypeScript interfaces
```

## Infraestrutura

- **Deploy:** Oracle Cloud VPS (free tier ARM) com IP público
- **Servidor:** Uvicorn (ASGI)
- **Config:** pydantic-settings + `.env`

## Decisoes Arquiteturais

| Decisao | Escolha | Motivo |
|---|---|---|
| LLM | GPT-4o-mini + Groq fallback | Custo-eficiente com resiliencia gratuita |
| TTS | ElevenLabs/OpenAI/Edge cascade | Qualidade premium com fallback gratuito |
| Busca Web | Tavily + DuckDuckGo | API otimizada com fallback sem custo |
| Classificacao | 2 chamadas LLM separadas | Controle sobre routing, debugging mais facil |
| Storage | Markdown no filesystem + SQLite | Compativel com Obsidian + dados estruturados |
| Busca | ChromaDB local | Zero custo, sem infra extra, reconstruivel |
| API style | REST + SSE streaming | Baixa latencia percebida para respostas longas |
| Email | Gmail API + triagem automatica | Integracao nativa com confirmacao de envio |
