# API

## Visão Geral

API REST com 3 endpoints: `POST /chat` (texto), `POST /voice` (áudio) e `GET /health`. Recebe input do usuário, processa via ATLAS e retorna resposta com personalidade.

8 intenções suportadas: `save_note`, `create_event`, `query_calendar`, `delete_event`, `log_habit`, `search`, `briefing`, `chat`.

## Autenticação

Header `X-API-Key` com chave configurada em `ATLAS_API_KEY` no `.env`.

## Endpoints

### POST /chat

Endpoint principal de interação com o ATLAS.

**Request:**
```json
{
  "message": "Marca reunião com João amanhã às 15h"
}
```

**Response (sucesso):**
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
  "response": "Algo deu errado ao tentar criar o evento. Provavelmente não é culpa minha.",
  "intent": "create_event",
  "error": "Google Calendar API unavailable"
}
```

**Headers:**
| Header | Valor | Obrigatório |
|---|---|---|
| `Content-Type` | `application/json` | Sim |
| `X-API-Key` | Chave de API | Sim |

**Códigos de status:**
| Código | Significado |
|---|---|
| 200 | Sucesso |
| 401 | API key inválida ou ausente |
| 422 | Body inválido |
| 500 | Erro interno |

### POST /voice

Endpoint de interação por voz. Recebe áudio, transcreve via Whisper, processa como /chat e retorna resposta com áudio TTS.

**Request:** `multipart/form-data`
| Campo | Tipo | Obrigatório |
|---|---|---|
| `audio` | Arquivo de áudio | Sim |

**Headers:**
| Header | Valor | Obrigatório |
|---|---|---|
| `X-API-Key` | Chave de API | Sim |

**Response (sucesso):**
```json
{
  "response": "Nota salva. Mais uma que provavelmente vai ficar esquecida.",
  "intent": "save_note",
  "actions": [...],
  "audio_base64": "<áudio TTS codificado em base64>"
}
```

**Fluxo interno:**
1. Recebe áudio → transcreve via OpenAI Whisper (pt-BR)
2. Texto transcrito → processa via pipeline ATLAS (igual /chat)
3. Resposta texto → gera áudio via OpenAI TTS (voz "onyx")
4. Retorna resposta + áudio em base64

**Códigos de status:**
| Código | Significado |
|---|---|
| 200 | Sucesso |
| 401 | API key inválida ou ausente |
| 500 | Erro interno (transcrição ou TTS) |

---

### GET /health

Health check simples.

**Response:**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

## Intenções e Actions

| Intent | Action type | Exemplo de details |
|---|---|---|
| `save_note` | `note_saved` | `{ path, title, category }` |
| `create_event` | `calendar_event_created` | `{ title, datetime, calendar_event_id }` |
| `query_calendar` | `calendar_events_listed` | `{ events: [...], period }` |
| `delete_event` | `calendar_event_deleted` | `{ title, date }` |
| `log_habit` | `habit_logged` | `{ habit, value, category }` |
| `search` | `search_completed` | `{ source, results_count }` |
| `briefing` | `briefing_generated` | `{ sections: [...] }` |
| `chat` | (nenhuma) | — |

## Exemplos de Uso

```bash
# Criar nota
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "Anota que preciso comprar remédio amanhã"}'

# Briefing do dia
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "O que tenho pra hoje?"}'

# Registrar hábito
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "Dormi 6 horas ontem"}'

# Pesquisar
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "O que eu anotei sobre o projeto X?"}'
```

## Exemplos Adicionais

```bash
# Deletar evento
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "Cancela a reunião de sexta"}'

# Enviar áudio
curl -X POST http://localhost:8000/voice \
  -H "X-API-Key: sua-chave" \
  -F "audio=@gravacao.webm"
```

## Evolução Planejada

- **Fase 2:** Streaming via SSE (`text/event-stream`) para resposta em tempo real
- **Fase 2:** Endpoint de dashboard (`GET /dashboard`)
