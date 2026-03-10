# Integracoes

## OpenAI API

**Tipo:** REST API
**Uso:** Classificacao de intencao, geracao de resposta, embeddings, STT, TTS
**Dependencia:** Alta — com fallback para Groq

### Modelos utilizados
| Modelo | Uso | Custo estimado |
|---|---|---|
| `gpt-4o-mini` | Chat completions (classificacao + resposta) | ~$0.15/1M tokens input |
| `text-embedding-3-small` | Embeddings para indexacao no ChromaDB | ~$0.02/1M tokens |
| `whisper-1` | Speech-to-text (transcricao de audio) | ~$0.006/minuto |
| `tts-1` | Text-to-speech (voz "onyx") | ~$15/1M caracteres |

### Padrao de uso
- 2 chamadas por request: classificacao + resposta com persona
- SDK: `openai` Python (`>=1.60`)
- Autenticacao: API key via `OPENAI_API_KEY` env var
- **Fallback:** Groq (gratuito) quando OpenAI falha

### Tratamento de falhas
- Timeout: 30s por chamada
- Rate limit: retry com backoff exponencial
- Erro: fallback para Groq, depois mensagem generica

---

## Google Calendar API

**Tipo:** REST API (Google Workspace)
**Uso:** CRUD de eventos do calendário
**Dependência:** Alta — briefing e gestão de agenda dependem dela

### Autenticação
- OAuth2 via `google-auth-oauthlib`
- Primeiro uso: abre navegador para consentimento
- Token salvo em `token.json` (auto-refresh)
- Scopes: `https://www.googleapis.com/auth/calendar`

### Operações
- `events().list()` — listar eventos
- `events().insert()` — criar evento
- `events().update()` — editar evento
- `events().delete()` — deletar evento

### Requisitos
- `credentials.json` do Google Cloud Console (OAuth 2.0 Client ID)
- Projeto no Google Cloud com Calendar API habilitada

---

## Tavily API

**Tipo:** REST API
**Uso:** Busca web otimizada para LLMs
**Dependencia:** Baixa — com fallback para DuckDuckGo

### Padrao de uso
- `search()` — retorna resultados estruturados
- `max_results=5` para limitar quantidade
- **Fallback:** DuckDuckGo (gratuito) quando Tavily falha ou nao configurado

### Autenticacao
- API key via `TAVILY_API_KEY` env var
- Free tier disponivel

---

## Groq API (Fallback LLM)

**Tipo:** REST API
**Uso:** Fallback gratuito para OpenAI
**Dependencia:** Opcional — ativado quando OpenAI falha

### Modelo
| Modelo | Uso | Custo |
|---|---|---|
| `llama-3.1-8b-instant` | Chat completions (fallback) | Gratuito |

### Configuracao
- API key via `GROQ_API_KEY` env var
- SDK: `groq` Python
- Ativado automaticamente em caso de falha do OpenAI

---

## ElevenLabs API (Premium TTS)

**Tipo:** REST API
**Uso:** Text-to-speech de alta qualidade
**Dependencia:** Opcional — usado em modo `audio_premium`

### Configuracao
| Variavel | Descricao |
|---|---|
| `ELEVENLABS_API_KEY` | API key |
| `ELEVENLABS_VOICE_ID` | ID da voz (default: "Adam") |

### Modelo
- `eleven_multilingual_v2` — suporta portugues
- Voice settings: stability=0.5, similarity_boost=0.75

### Cascata de TTS (audio_premium)
1. ElevenLabs (premium)
2. OpenAI TTS (fallback pago)
3. Edge TTS (fallback gratuito)

---

## Edge TTS (Gratuito)

**Tipo:** Biblioteca local (Microsoft Edge)
**Uso:** Text-to-speech gratuito
**Dependencia:** Fallback final para TTS

### Configuracao
| Variavel | Descricao |
|---|---|
| `EDGE_TTS_VOICE` | Voz (default: "pt-BR-AntonioNeural") |

### Caracteristicas
- Totalmente gratuito
- Voz masculina brasileira de qualidade
- Usado em modo `audio` ou como fallback final

---

## DuckDuckGo Search (Fallback)

**Tipo:** Biblioteca local
**Uso:** Busca web gratuita
**Dependencia:** Fallback para Tavily

### Caracteristicas
- Sem API key necessaria
- Ativado quando Tavily falha ou nao esta configurado
- Biblioteca: `duckduckgo-search`

---

## Gmail API

**Tipo:** REST API (Google Workspace)
**Uso:** Leitura, envio e triagem de emails
**Dependencia:** Media — funcionalidade de email depende dela

### Autenticacao
- OAuth2 (mesmo fluxo do Calendar)
- Scopes adicionais: `https://www.googleapis.com/auth/gmail.modify`

### Operacoes
- `messages().list()` — listar emails
- `messages().get()` — ler email completo
- `messages().send()` — enviar email
- `messages().trash()` — mover para lixeira

### Triagem Automatica
- Background task limpa spam/newsletters
- Executa periodicamente
- Endpoint `DELETE /email-alerts` para limpar alertas

---

## ChromaDB

**Tipo:** Banco vetorial local (embedded)
**Uso:** Busca semântica nas notas do vault Obsidian
**Dependência:** Alta — busca no vault depende dela

### Configuração
- `PersistentClient(path="./chroma_db")` — dados persistem no disco
- Collection: `vault_notes`
- IDs: hash SHA256 do conteúdo do arquivo

### Indexação incremental
- `upsert()` — adiciona novo ou atualiza existente baseado no ID
- Roda no startup + opcionalmente via filesystem watcher
- Reconstruível a partir do vault (não é source of truth)

---

## Obsidian Vault

**Tipo:** Filesystem (markdown)
**Uso:** Source of truth para todas as notas, hábitos, pesquisas
**Dependência:** Crítica

### Acesso
- Direto via `pathlib` + `python-frontmatter`
- Backend e vault na mesma máquina
- Compatível com Obsidian app rodando simultaneamente

### Estrutura
```
vault/
├── daily/           # YYYY-MM-DD.md
├── inbox/           # Notas não categorizadas
├── projects/        # Notas por projeto
├── people/          # Notas por pessoa
├── habits/
│   ├── health/      # Sono, exercício, humor
│   └── productivity/
├── research/        # Pesquisas salvas
├── insights/        # Padrões detectados (Fase 2)
└── templates/       # Templates markdown
```

## Mobile App (React Native / Expo)

**Tipo:** App Android (React Native + Expo SDK 54)
**Uso:** Interface de chat principal com ATLAS
**Dependência:** Consumidor da API — não é dependência do backend

### Comunicação com Backend
- HTTP REST via `fetch`
- Endpoints consumidos: `POST /chat`, `POST /voice`, `GET /health`
- Autenticação: header `X-API-Key`
- **Dev:** via ngrok tunnel (URL em `src/api/atlas.ts`)
- **Produção:** via IP público da Oracle Cloud VPS

### Funcionalidades do App
- Chat com texto e voz
- Action cards visuais por tipo de ação
- Indicador de status online/offline
- Gravação de áudio (Expo AV) + envio para transcrição

---

## Variaveis de Ambiente

```env
# Obrigatorias
OPENAI_API_KEY=sk-...
ATLAS_API_KEY=sua-chave-para-proteger-o-endpoint

# Google (Calendar + Gmail)
GOOGLE_CREDENTIALS_PATH=./credentials.json
GOOGLE_TOKEN_PATH=./token.json

# Paths
VAULT_PATH=./vault
CHROMA_DB_PATH=./chroma_db
MEMORY_DB_PATH=./memory.db

# Opcionais - APIs pagas
TAVILY_API_KEY=tvly-...              # Busca web (fallback: DuckDuckGo)
ELEVENLABS_API_KEY=...               # TTS premium
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB  # Voz "Adam"

# Opcionais - Fallbacks gratuitos
GROQ_API_KEY=gsk-...                 # LLM fallback
GROQ_MODEL=llama-3.1-8b-instant

# TTS gratuito
EDGE_TTS_VOICE=pt-BR-AntonioNeural   # Voz brasileira

# Modo de resposta
RESPONSE_MODE=text                    # text | audio | audio_premium

# Outros
TIMEZONE=America/Sao_Paulo
SESSION_EXPIRY_HOURS=24
```

## Hierarquia de Fallbacks

```
LLM:     OpenAI GPT-4o-mini  -->  Groq Llama 3.1 (gratuito)
TTS:     ElevenLabs  -->  OpenAI TTS  -->  Edge TTS (gratuito)
Search:  Tavily  -->  DuckDuckGo (gratuito)
```
