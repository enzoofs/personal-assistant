# ADR-006: Sistema de Fallbacks Gratuitos

## Status
Aceito

## Contexto

O ATLAS depende de múltiplos serviços externos pagos:
- OpenAI GPT-4o-mini para LLM (classificação e resposta)
- OpenAI Whisper para transcrição
- ElevenLabs/OpenAI para TTS
- Tavily para busca web

Riscos identificados:
1. **Custo**: Uso diário pode acumular custos significativos
2. **Disponibilidade**: APIs podem ficar indisponíveis temporariamente
3. **Rate limits**: Uso intenso pode atingir limites
4. **Dependência**: Sistema fica inutilizável se API principal falhar

## Decisão

Implementar sistema de fallbacks gratuitos para todos os serviços críticos:

| Serviço | Principal (pago) | Fallback (gratuito) |
|---|---|---|
| LLM | OpenAI GPT-4o-mini | Groq Llama 3.1 8B |
| TTS | ElevenLabs → OpenAI | Edge TTS (Microsoft) |
| Busca Web | Tavily | DuckDuckGo |

### Implementação

**LLM Fallback (Groq)**
```python
async def chat_completion(...):
    try:
        return await _client.chat.completions.create(...)
    except Exception:
        groq = _get_groq_client()
        if groq:
            return await groq.chat.completions.create(...)
        raise
```

**TTS Cascade**
```python
async def text_to_speech(text: str) -> bytes | None:
    mode = settings.response_mode
    if mode == "text":
        return None
    if mode == "audio":
        return await _edge_tts(text)  # Free only
    # audio_premium: ElevenLabs → OpenAI → Edge TTS
    ...
```

**Search Fallback**
```python
def _web_search(query: str, max_results: int = 5):
    if settings.tavily_api_key:
        try:
            return _tavily_search(query, max_results)
        except:
            pass
    return _duckduckgo_search(query, max_results)
```

### Configuração

```env
# Groq (free tier: 30 req/min)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-8b-instant

# Edge TTS (free, no key required)
EDGE_TTS_VOICE=pt-BR-AntonioNeural

# Response mode: text|audio|audio_premium
RESPONSE_MODE=text
```

## Consequências

### Positivas
- **Resiliência**: Sistema continua funcionando mesmo com APIs pagas indisponíveis
- **Custo zero opcional**: Pode operar 100% grátis se necessário
- **Degradação graciosa**: Qualidade reduz, mas funcionalidade mantida
- **Flexibilidade**: Usuário escolhe trade-off custo/qualidade

### Negativas
- **Complexidade**: Mais código de error handling
- **Qualidade variável**: Groq/Edge TTS são inferiores às opções pagas
- **Latência**: Fallbacks podem ser mais lentos
- **Manutenção**: Mais serviços para monitorar

### Neutras
- **Rate limits diferentes**: Groq tem 30 req/min no free tier
- **Vozes diferentes**: Edge TTS tem sotaque diferente de ElevenLabs

## Alternativas Consideradas

1. **Só usar APIs pagas**: Descartado — risco de indisponibilidade e custo
2. **Self-hosted LLM**: Descartado — requer GPU, complexidade alta
3. **Caching agressivo**: Implementado parcialmente (embeddings), não resolve fallback
4. **Circuit breaker**: Pode complementar, mas não substitui fallback

## Referências

- Groq Free Tier: https://console.groq.com/
- Edge TTS: https://github.com/rany2/edge-tts
- DuckDuckGo Search: https://pypi.org/project/duckduckgo-search/
