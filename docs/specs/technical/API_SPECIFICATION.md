# Especificação da API — ATLAS

## Visão Geral

API REST com 3 endpoints. Autenticação via header `X-API-Key`. Servidor Uvicorn (ASGI) na porta 8000.

## Autenticação

Todas as rotas exceto `/health` requerem o header:
```
X-API-Key: <valor configurado em ATLAS_API_KEY no .env>
```

Resposta para key inválida/ausente: `401 Unauthorized`

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
| `log_habit` | `habit_logged` | `{ habit, value, category }` |
| `search` | `search_completed` | `{ source, results_count }` |
| `briefing` | `briefing_generated` | `{ sections: [...] }` |
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

### GET /health

Health check sem autenticação.

**Response (200):**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

## Códigos de Status

| Código | Significado |
|---|---|
| 200 | Sucesso |
| 401 | API key inválida ou ausente |
| 422 | Body inválido (validação Pydantic) |
| 500 | Erro interno |

## Schemas (Pydantic)

```python
class ChatRequest(BaseModel):
    message: str

class ActionResult(BaseModel):
    type: str
    details: dict

class ChatResponse(BaseModel):
    response: str
    intent: str
    actions: list[ActionResult] = []
    error: str | None = None
```

## Evolução Planejada

- **Fase 2:** Streaming via SSE (`text/event-stream`)
- **Fase 2:** Endpoint de dashboard (`GET /dashboard`)
- **Fase 2:** Endpoints de áudio aprimorados
