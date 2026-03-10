# ADR-007: Antecipação de Streaming SSE para Fase 1.5

## Status
Aceito

## Contexto

O pipeline original do ATLAS faz 2 chamadas LLM sequenciais por requisição:
1. Classificação de intenção (GPT-4o-mini)
2. Geração de resposta com personalidade (GPT-4o-mini)

Isso resulta em latência de 2.5-4.5 segundos antes do usuário ver qualquer resposta, criando uma experiência de "espera" frustrante, especialmente em mobile.

O streaming estava planejado para Fase 2, mas a latência percebida era o principal ponto de fricção no uso diário.

## Decisão

Antecipar a implementação de streaming SSE da Fase 2 para a Fase 1.5, priorizando UX sobre completude de features.

### Implementação

**Novo endpoint `/chat/stream`**
```python
@app.post("/chat/stream")
async def chat_stream(body: ChatRequest):
    return StreamingResponse(
        process_stream(body.message, body.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
```

**Streaming no OpenAI client**
```python
async def chat_completion_stream(messages, model=None, temperature=0.7):
    async for chunk in await _client.chat.completions.create(
        model=model or settings.openai_model,
        messages=messages,
        temperature=temperature,
        stream=True,
    ):
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

**Formato SSE**
```
data: {"type": "token", "content": "Olá"}\n\n
data: {"type": "token", "content": ", "}\n\n
data: {"type": "token", "content": "Enzo"}\n\n
data: {"type": "done", "intent": "chat", "actions": []}\n\n
```

### Arquivos Modificados

| Arquivo | Mudança |
|---|---|
| `atlas/main.py` | Novo endpoint `/chat/stream` |
| `atlas/orchestrator.py` | Função `process_stream()` com yield |
| `atlas/services/openai_client.py` | `chat_completion_stream()` |
| `atlas/persona/atlas.py` | `generate_response_stream()` |

## Consequências

### Positivas
- **TTFB ~500ms**: Usuário vê resposta começando em menos de 1 segundo
- **UX percebida**: Sensação de resposta instantânea mesmo com latência total similar
- **Feedback visual**: App pode mostrar texto aparecendo progressivamente
- **Fallback integrado**: Streaming também funciona com Groq (fallback gratuito)

### Negativas
- **Complexidade**: Dois endpoints para manter (`/chat` e `/chat/stream`)
- **Mobile mais complexo**: App precisa processar `EventSource` / chunks
- **Error handling diferente**: Erros mid-stream são mais difíceis de tratar
- **Testes mais difíceis**: Testar streaming requer mocks assíncronos especiais

### Neutras
- **Latência total similar**: O tempo total não muda muito, só a percepção
- **Compatibilidade**: Endpoint síncrono `/chat` mantido para compatibilidade

## Métricas

| Métrica | Antes | Depois |
|---|---|---|
| Tempo até primeiro byte (TTFB) | 2.5-4.5s | ~500ms |
| Tempo total | 2.5-4.5s | 2-3s |
| UX percebida | Espera frustrante | Resposta imediata |

## Alternativas Consideradas

1. **Manter para Fase 2**: Descartado — latência era o principal ponto de fricção
2. **Só otimizar backend**: Implementado parcialmente (parallelização), mas não resolve UX
3. **WebSocket**: Mais complexo, SSE é suficiente para unidirecional
4. **Chunked response sem SSE**: Menos padronizado, SSE tem melhor suporte em browsers

## Referências

- Server-Sent Events: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
- FastAPI StreamingResponse: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
- OpenAI Streaming: https://platform.openai.com/docs/api-reference/streaming
