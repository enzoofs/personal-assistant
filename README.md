# ATLAS

Assistente pessoal com IA — centraliza calendário, email, notas (Obsidian), hábitos e lista de compras em uma interface de chat com personalidade.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688)
![React Native](https://img.shields.io/badge/React%20Native-Expo%20SDK%2054-61DAFB)

## Funcionalidades

- **Classificação de intent** — detecta automaticamente o que você quer (salvar nota, criar evento, logar hábito, etc.) via GPT-4o-mini
- **Obsidian Vault** — salva notas categorizadas com frontmatter, busca semântica via ChromaDB
- **Google Calendar** — cria, edita e consulta eventos com linguagem natural ("amanhã às 15h")
- **Gmail** — lê, envia e descarta emails com etapa de confirmação
- **Hábitos** — registra sono, exercício, humor e hábitos customizados
- **Briefing diário** — agregado de eventos, notas recentes, hábitos e emails importantes
- **Lista de compras** — adiciona/remove itens por categoria
- **Insights proativos** — detecta padrões em hábitos e produtividade, gera observações
- **Voz** — speech-to-text (Whisper) e text-to-speech (ElevenLabs → OpenAI → Edge TTS)
- **Memória** — mantém contexto da conversa e extrai fatos automaticamente

## Arquitetura

```
Mensagem do usuário
    ↓
Intent Classifier (GPT-4o-mini)
    ↓
Router → Tool Handler
    ├── Obsidian Manager    (notas)
    ├── Calendar Manager    (eventos)
    ├── Habit Tracker       (hábitos)
    ├── Gmail Client        (email)
    ├── Search Engine       (vault + web)
    └── Briefing Generator  (resumo diário)
    ↓
Response Generator (GPT-4o-mini + persona ATLAS)
```

## Stack

| Componente | Tecnologia |
|---|---|
| Backend | FastAPI + Python 3.12 |
| LLM | OpenAI GPT-4o-mini (fallback: Groq) |
| Embeddings | ChromaDB + text-embedding-3-small |
| Calendar/Email | Google Calendar API + Gmail API (OAuth2) |
| TTS | ElevenLabs → OpenAI → Edge TTS (cascade) |
| Mobile | React Native (Expo SDK 54) |
| Deploy | Docker + Oracle Cloud |

## Setup

```bash
# Backend
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # Configurar API keys
uvicorn atlas.main:app --reload --port 8000

# Mobile
cd mobile && npm install && npm run android
```

## Personalidade

ATLAS tem uma persona inspirada no Jarvis — sofisticado, sarcástico e direto. Observa padrões e faz comentários não solicitados sobre seus hábitos.

> "Terceiro dia consecutivo dormindo pouco. Experimento ousado."

## Estrutura

```
atlas/
├── main.py              # FastAPI endpoints
├── orchestrator.py      # Pipeline: classify → route → execute → respond
├── intent/              # Classificação de intent
├── tools/               # Handlers (obsidian, calendar, email, habits...)
├── persona/             # System prompt + geração de resposta
├── vault/               # Gerenciamento do Obsidian vault
├── services/            # Clientes Google, OpenAI
├── memory/              # Memória persistente
└── proactive/           # Insights e análise de padrões

mobile/
├── src/screens/         # Home, Dashboard, Settings
├── src/components/      # Chat, MicButton, etc.
└── src/context/         # Theme, Settings, Dashboard
```
