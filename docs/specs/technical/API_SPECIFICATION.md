# Especificacao da API - ATLAS

## Visao Geral

API REST com multiplos endpoints, incluindo streaming via SSE. Autenticacao via header `X-API-Key`. Servidor Uvicorn (ASGI) na porta 8000.

**Categorias de Endpoints:**
- **Core:** `/chat`, `/chat/stream`, `/voice`, `/speak`, `/health`
- **Settings:** `/settings`
- **Shopping:** `/shopping/*`
- **Vault:** `/vault/*`
- **Email:** `/email-alerts`
- **Dashboard:** `/dashboard`

## Autenticacao

Todas as rotas exceto `/health` requerem o header:
```
X-API-Key: <valor configurado em ATLAS_API_KEY no .env>
```

Resposta para key invalida/ausente: `401 Unauthorized`

## Rate Limiting

- **Limite:** 30 requests por minuto por IP
- **Response:** `429 Too Many Requests`

## Endpoints

### POST /chat

Endpoint principal. Recebe texto, processa via pipeline ATLAS, retorna resposta com personalidade.

**Request:**
```json
{
  "message": "Marca reunião com João amanhã às 15h"
}
```

**Response (200):**
```json
{
  "response": "Reunião com o João marcada pra amanhã às 15h. Tenta não cancelar dessa vez.",
  "intent": "create_event",
  "actions": [
    {
      "type": "calendar_event_created",
      "details": {
        "title": "Reunião com João",
        "datetime": "2026-02-03T15:00:00",
        "calendar_event_id": "abc123"
      }
    }
  ]
}
```

**Response (erro):**
```json
{
  "response": "Algo deu errado ao tentar criar o evento.",
  "intent": "create_event",
  "error": "Google Calendar API unavailable"
}
```

**Tipos de action por intent:**

| Intent | Action type | Details |
|---|---|---|
| `save_note` | `note_saved` | `{ path, title, category }` |
| `create_event` | `calendar_event_created` | `{ title, datetime, calendar_event_id }` |
| `query_calendar` | `calendar_events_listed` | `{ events: [...], period }` |
| `delete_event` | `calendar_event_deleted` | `{ title, date }` |
| `edit_event` | `calendar_event_updated` | `{ title, changes }` |
| `log_habit` | `habit_logged` | `{ habit, value, category }` |
| `read_email` | `read_email` | `{ query, count, emails: [...] }` |
| `send_email` | `send_email_pending` | `{ to, subject, status }` |
| `confirm_send_email` | `send_email` | `{ to, subject, message_id }` |
| `trash_email` | `trash_email` | `{ count, emails: [...] }` |
| `search` | `search` | `{ query, source, vault_count, web_count }` |
| `briefing` | `briefing_generated` | `{ sections: [...] }` |
| `shopping_add` | `shopping_add` | `{ items: [...], category, count }` |
| `shopping_list` | `shopping_list` | `{ items: [...], count }` |
| `shopping_complete` | `shopping_complete` | `{ item_id, item }` |
| `chat` | (nenhuma) | — |

### POST /voice

Recebe áudio, transcreve via Whisper, processa como /chat, retorna resposta + áudio TTS.

**Request:** `multipart/form-data` com campo `audio` (arquivo de áudio)

**Response (200):**
```json
{
  "response": "Texto da resposta do ATLAS",
  "intent": "...",
  "actions": [...],
  "audio_base64": "<áudio TTS em base64>"
}
```

### POST /chat/stream

Streaming de resposta via Server-Sent Events.

**Request:**
```json
{
  "message": "Explica machine learning",
  "session_id": "user-123"
}
```

**Response:** `text/event-stream`
```
data: {"type": "token", "content": "Machine"}

data: {"type": "token", "content": " learning"}

data: {"type": "done", "intent": "chat", "actions": []}
```

**Headers:**
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

---

### POST /speak

Text-to-speech direto baseado no `response_mode` configurado.

**Request:**
```json
{
  "text": "Texto para converter em audio"
}
```

**Response (200):**
```json
{
  "audio_base64": "<MP3 em base64 ou null>",
  "mode": "audio_premium"
}
```

---

### GET /settings

Retorna configuracoes atuais.

**Response (200):**
```json
{
  "response_mode": "audio_premium",
  "available_modes": ["text", "audio", "audio_premium"]
}
```

### PATCH /settings

Atualiza configuracoes em runtime.

**Request:**
```json
{
  "response_mode": "audio"
}
```

**Response (200):**
```json
{
  "response_mode": "audio"
}
```

---

### GET /health

Health check com status dos servicos (sem autenticacao).

**Response (200):**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "services": {
    "google": "ok",
    "tavily": "ok"
  }
}
```

---

## Shopping List Endpoints

### GET /shopping

Lista itens pendentes.

**Response (200):**
```json
{
  "items": [
    {"id": 1, "item": "Leite", "category": "mercado", "quantity": "2L", "completed": false}
  ],
  "count": 1
}
```

### POST /shopping

Adiciona item.

**Request:**
```json
{
  "item": "Cafe",
  "quantity": "500g",
  "category": "mercado"
}
```

### PATCH /shopping/{item_id}

Marca como comprado/nao comprado.

**Request:**
```json
{
  "completed": true
}
```

### DELETE /shopping/{item_id}

Remove item especifico.

### DELETE /shopping

Remove todos os itens completados.

---

## Vault Endpoints

### GET /vault/search

Busca semantica no vault.

**Query params:** `query` (string), `limit` (int, default 5)

### GET /vault/stats

Estatisticas do vault.

### POST /vault/voice-capture

Processa transcricao em nota estruturada.

**Request:**
```json
{
  "transcription": "Texto transcrito",
  "quick": false
}
```

### GET /vault/connections/{note_path}

Sugestoes de conexoes para nota.

### GET /vault/orphans

Notas sem conexoes.

### GET /vault/graph

Grafo de conexoes para visualizacao.

### POST /vault/reindex

Reindexa vault para busca semantica.

---

## Dashboard & Email

### GET /dashboard

Dados agregados para dashboard.

### DELETE /email-alerts

Limpa alertas de email.

---

## Codigos de Status

| Codigo | Significado |
|---|---|
| 200 | Sucesso |
| 400 | Request invalido (parametro faltando) |
| 401 | API key invalida ou ausente |
| 404 | Recurso nao encontrado |
| 422 | Body invalido (validacao Pydantic) |
| 429 | Rate limit excedido |
| 500 | Erro interno |

## Schemas (Pydantic)

```python
class IntentType(str, Enum):
    SAVE_NOTE = "save_note"
    CREATE_EVENT = "create_event"
    QUERY_CALENDAR = "query_calendar"
    DELETE_EVENT = "delete_event"
    EDIT_EVENT = "edit_event"
    LOG_HABIT = "log_habit"
    READ_EMAIL = "read_email"
    SEND_EMAIL = "send_email"
    CONFIRM_SEND_EMAIL = "confirm_send_email"
    TRASH_EMAIL = "trash_email"
    SEARCH = "search"
    BRIEFING = "briefing"
    SHOPPING_ADD = "shopping_add"
    SHOPPING_LIST = "shopping_list"
    SHOPPING_COMPLETE = "shopping_complete"
    CHAT = "chat"

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ActionResult(BaseModel):
    type: str
    details: dict = {}

class ChatResponse(BaseModel):
    response: str
    intent: str
    actions: list[ActionResult] = []
    error: str | None = None
```

## Modos de Resposta (TTS)

| Mode | Provider | Custo |
|---|---|---|
| `text` | Nenhum (audio desabilitado) | Gratuito |
| `audio` | Edge TTS | Gratuito |
| `audio_premium` | ElevenLabs -> OpenAI -> Edge TTS | Pago |

## Sistema de Fallbacks

```
LLM:     OpenAI  -->  Groq (gratuito)
TTS:     ElevenLabs  -->  OpenAI  -->  Edge TTS (gratuito)
Search:  Tavily  -->  DuckDuckGo (gratuito)
```
