# API

## Visao Geral

API REST com multiplos endpoints para interacao com o ATLAS. Suporta texto, audio, streaming via SSE, e operacoes especializadas (shopping, vault, email).

**Endpoints principais:**
- `POST /chat` — Interacao por texto
- `POST /chat/stream` — Streaming via Server-Sent Events
- `POST /voice` — Interacao por audio (Whisper STT + TTS)
- `POST /speak` — Text-to-speech direto
- `GET/PATCH /settings` — Configuracoes de runtime
- `GET /health` — Health check
- `/shopping/*` — Lista de compras (CRUD)
- `/vault/*` — Operacoes no vault Obsidian

**16 intents suportados:** `save_note`, `create_event`, `query_calendar`, `delete_event`, `edit_event`, `log_habit`, `read_email`, `send_email`, `confirm_send_email`, `trash_email`, `search`, `briefing`, `shopping_add`, `shopping_list`, `shopping_complete`, `chat`.

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

### POST /chat/stream

Streaming de resposta via Server-Sent Events (SSE). Menor latencia percebida para respostas longas.

**Request:**
```json
{
  "message": "Explica o que e machine learning",
  "session_id": "user-123"
}
```

**Response:** `text/event-stream`
```
data: {"type": "token", "content": "Machine"}

data: {"type": "token", "content": " learning"}

data: {"type": "token", "content": " e"}

data: {"type": "done", "intent": "chat", "actions": []}

```

**Headers de resposta:**
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

---

### POST /speak

Converte texto para audio usando o modo de resposta configurado.

**Request:**
```json
{
  "text": "Ola, como posso ajudar?"
}
```

**Response:**
```json
{
  "audio_base64": "<audio MP3 em base64>",
  "mode": "audio_premium"
}
```

**Modos de TTS:**
| Mode | Provider | Custo |
|---|---|---|
| `text` | Nenhum (retorna null) | Gratuito |
| `audio` | Edge TTS | Gratuito |
| `audio_premium` | ElevenLabs -> OpenAI -> Edge TTS | Pago |

---

### GET /settings

Retorna configuracoes atuais do ATLAS.

**Response:**
```json
{
  "response_mode": "audio_premium",
  "available_modes": ["text", "audio", "audio_premium"]
}
```

### PATCH /settings

Atualiza configuracoes em runtime (nao persiste no .env).

**Request:**
```json
{
  "response_mode": "audio"
}
```

**Response:**
```json
{
  "response_mode": "audio"
}
```

---

### GET /health

Health check com status dos servicos.

**Response:**
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

## Shopping List API

### GET /shopping

Lista itens pendentes da lista de compras.

**Response:**
```json
{
  "items": [
    {"id": 1, "item": "Leite", "category": "mercado", "quantity": "2L"},
    {"id": 2, "item": "Pao", "category": "mercado", "quantity": null}
  ],
  "count": 2
}
```

### POST /shopping

Adiciona item a lista de compras.

**Request:**
```json
{
  "item": "Cafe",
  "quantity": "500g",
  "category": "mercado"
}
```

**Response:**
```json
{
  "id": 3,
  "item": "Cafe",
  "category": "mercado"
}
```

### PATCH /shopping/{item_id}

Marca item como comprado/nao comprado.

**Request:**
```json
{
  "completed": true
}
```

### DELETE /shopping/{item_id}

Remove item da lista.

### DELETE /shopping

Remove todos os itens completados.

**Response:**
```json
{
  "status": "cleared",
  "count": 5
}
```

---

## Vault API

### GET /vault/search?query=...&limit=5

Busca semantica no vault.

### GET /vault/stats

Estatisticas do vault (contagem de notas por categoria).

### POST /vault/voice-capture

Processa transcricao de voz em nota estruturada.

**Request:**
```json
{
  "transcription": "Lembrar de revisar o contrato do projeto X ate sexta",
  "quick": false
}
```

### GET /vault/connections/{note_path}

Sugestoes de conexoes para uma nota.

### POST /vault/reindex

Reindexa o vault para busca semantica.

---

## Intents e Actions

### Notas e Vault
| Intent | Action type | Exemplo de details |
|---|---|---|
| `save_note` | `note_saved` | `{ path, title, category }` |
| `search` | `search` | `{ query, source, vault_count, web_count }` |
| `briefing` | `briefing_generated` | `{ sections: [...] }` |

### Calendario
| Intent | Action type | Exemplo de details |
|---|---|---|
| `create_event` | `calendar_event_created` | `{ title, datetime, calendar_event_id }` |
| `query_calendar` | `calendar_events_listed` | `{ events: [...], period }` |
| `delete_event` | `calendar_event_deleted` | `{ title, date }` |
| `edit_event` | `calendar_event_updated` | `{ title, changes }` |

### Habitos
| Intent | Action type | Exemplo de details |
|---|---|---|
| `log_habit` | `habit_logged` | `{ habit, value, category }` |

### Shopping List
| Intent | Action type | Exemplo de details |
|---|---|---|
| `shopping_add` | `shopping_add` | `{ items: [...], category, count }` |
| `shopping_list` | `shopping_list` | `{ items: [...], count }` |
| `shopping_complete` | `shopping_complete` | `{ item_id, item }` |

### Email
| Intent | Action type | Exemplo de details |
|---|---|---|
| `read_email` | `read_email` | `{ query, count, emails: [...] }` |
| `send_email` | `send_email_pending` | `{ to, subject, status: "pending" }` |
| `confirm_send_email` | `send_email` | `{ to, subject, message_id }` |
| `trash_email` | `trash_email` | `{ count, emails: [...] }` |

### Outros
| Intent | Action type | Exemplo de details |
|---|---|---|
| `chat` | (nenhuma) | — |

## Exemplos de Uso

```bash
# Criar nota
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "Anota que preciso comprar remedio amanha"}'

# Briefing do dia
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "O que tenho pra hoje?"}'

# Registrar habito
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "Dormi 6 horas ontem"}'

# Pesquisar
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "O que eu anotei sobre o projeto X?"}'

# Lista de compras
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "Adiciona leite e pao na lista de compras"}'

# Ler emails
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "Mostra meus emails nao lidos"}'

# Streaming (SSE)
curl -N http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "Explica o que e machine learning"}'

# Text-to-speech direto
curl -X POST http://localhost:8000/speak \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"text": "Ola, tudo bem?"}'

# Alterar modo de resposta
curl -X PATCH http://localhost:8000/settings \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"response_mode": "audio_premium"}'
```

## Exemplos Adicionais

```bash
# Deletar evento
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"message": "Cancela a reuniao de sexta"}'

# Enviar audio
curl -X POST http://localhost:8000/voice \
  -H "X-API-Key: sua-chave" \
  -F "audio=@gravacao.webm"

# Shopping list via REST
curl http://localhost:8000/shopping -H "X-API-Key: sua-chave"
curl -X POST http://localhost:8000/shopping \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sua-chave" \
  -d '{"item": "Cafe", "category": "mercado"}'
```

## Rate Limiting

- **Limite:** 30 requests por minuto por IP
- **Response:** `429 Too Many Requests` quando excedido
