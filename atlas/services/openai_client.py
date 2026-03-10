import logging
from functools import lru_cache
from typing import AsyncIterator

import httpx
from openai import AsyncOpenAI

from atlas.config import settings

logger = logging.getLogger(__name__)

_client = AsyncOpenAI(api_key=settings.openai_api_key)

# Groq client (lazy initialization)
_groq_client = None


def _get_groq_client():
    """Get or create Groq client."""
    global _groq_client
    if _groq_client is None and settings.groq_api_key:
        from groq import AsyncGroq
        _groq_client = AsyncGroq(api_key=settings.groq_api_key)
    return _groq_client


# Cache for embeddings (max 500 entries)
_embedding_cache: dict[str, list[float]] = {}
_EMBEDDING_CACHE_MAX = 500


async def chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
) -> str:
    """Chat completion with Groq fallback."""
    try:
        response = await _client.chat.completions.create(
            model=model or settings.openai_model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.warning("OpenAI chat failed: %s", e)
        groq = _get_groq_client()
        if groq:
            logger.info("Falling back to Groq")
            response = await groq.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        raise


async def chat_completion_stream(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
) -> AsyncIterator[str]:
    """Stream chat completion tokens with Groq fallback."""
    try:
        stream = await _client.chat.completions.create(
            model=model or settings.openai_model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        logger.warning("OpenAI stream failed: %s", e)
        groq = _get_groq_client()
        if groq:
            logger.info("Falling back to Groq stream")
            stream = await groq.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            raise


async def get_embedding(text: str) -> list[float]:
    """Get embedding for a single text, with caching."""
    if text in _embedding_cache:
        return _embedding_cache[text]

    response = await _client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    embedding = response.data[0].embedding

    # Cache management
    if len(_embedding_cache) >= _EMBEDDING_CACHE_MAX:
        # Remove oldest entry
        oldest = next(iter(_embedding_cache))
        del _embedding_cache[oldest]
    _embedding_cache[text] = embedding

    return embedding


async def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Get embeddings for multiple texts in a single API call."""
    if not texts:
        return []

    # Check cache first
    results = [None] * len(texts)
    texts_to_fetch = []
    indices_to_fetch = []

    for i, text in enumerate(texts):
        if text in _embedding_cache:
            results[i] = _embedding_cache[text]
        else:
            texts_to_fetch.append(text)
            indices_to_fetch.append(i)

    # Fetch missing embeddings in batch
    if texts_to_fetch:
        response = await _client.embeddings.create(
            model="text-embedding-3-small",
            input=texts_to_fetch,
        )
        for j, data in enumerate(response.data):
            idx = indices_to_fetch[j]
            embedding = data.embedding
            results[idx] = embedding
            # Cache
            if len(_embedding_cache) < _EMBEDDING_CACHE_MAX:
                _embedding_cache[texts_to_fetch[j]] = embedding

    return results


async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """Transcribe audio using OpenAI Whisper."""
    response = await _client.audio.transcriptions.create(
        model="whisper-1",
        file=(filename, audio_bytes),
        language="pt",
    )
    return response.text


async def text_to_speech(text: str) -> bytes | None:
    """Convert text to speech based on response_mode setting.

    Modes:
    - "text": Returns None (audio disabled)
    - "audio": Uses Edge TTS (free)
    - "audio_premium": ElevenLabs → OpenAI → Edge TTS cascade
    """
    mode = settings.response_mode

    if mode == "text":
        return None

    if mode == "audio":
        # Free mode: Edge TTS only
        return await _edge_tts(text)

    # audio_premium: full cascade
    if settings.elevenlabs_api_key:
        try:
            return await _elevenlabs_tts(text)
        except Exception as e:
            logger.warning("ElevenLabs TTS failed: %s", e)

    # Fallback to OpenAI TTS
    try:
        response = await _client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text,
        )
        return response.content
    except Exception as e:
        logger.warning("OpenAI TTS failed, falling back to Edge TTS: %s", e)

    # Final fallback: Edge TTS (free)
    return await _edge_tts(text)


async def _elevenlabs_tts(text: str) -> bytes:
    """Generate speech using ElevenLabs API."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": settings.elevenlabs_api_key,
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.3,
            "use_speaker_boost": True,
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.content


async def _edge_tts(text: str) -> bytes:
    """Generate speech using Microsoft Edge TTS (free)."""
    import edge_tts
    import io

    communicate = edge_tts.Communicate(text, settings.edge_tts_voice)
    audio_data = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.write(chunk["data"])
    return audio_data.getvalue()
