# Stack Tecnológica

## Linguagem e Runtime

- **Python 3.12+** — Ecossistema AI maduro, tipagem robusta, async nativo

## Framework Principal

- **FastAPI** (`>=0.115`) — API REST async, validação automática via Pydantic, docs OpenAPI grátis

## LLM e AI

| Componente | Tecnologia | Uso |
|---|---|---|
| Chat/Raciocínio | OpenAI GPT-4o-mini | Classificação de intenção + geração de resposta |
| Embeddings | OpenAI text-embedding-3-small | Indexação semântica do vault |
| Busca vetorial | ChromaDB (`>=0.6`, local) | Busca semântica nas notas do Obsidian |
| Busca web | Tavily API | Pesquisa web otimizada para LLMs |

## Storage

- **Obsidian vault** (markdown no filesystem) — Source of truth de todas as notas
- **ChromaDB** (persistente, local) — Índice vetorial reconstruível a partir do vault
- Sem banco de dados relacional — dados vivem como markdown com frontmatter YAML

## Integrações Externas

- **Google Calendar API** — OAuth2, CRUD de eventos
- **OpenAI API** — Chat completions + embeddings
- **Tavily API** — Busca web contextualizada

## Dependências Python

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

## Decisões Arquiteturais

| Decisão | Escolha | Motivo |
|---|---|---|
| LLM | GPT-4o-mini | Custo-eficiente (~$0.15/1M tokens), qualidade suficiente |
| Classificação | 2 chamadas LLM separadas | Controle sobre routing, debugging mais fácil |
| Storage | Markdown no filesystem | Compatível com Obsidian, portável, legível |
| Busca | ChromaDB local | Zero custo, sem infra extra, reconstruível |
| API style | REST síncrono (MVP) | Simplicidade. Streaming planejado para Fase 2 |
