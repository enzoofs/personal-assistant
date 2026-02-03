from functools import lru_cache
from typing import AsyncIterator

from openai import AsyncOpenAI

from atlas.config import settings

_client = AsyncOpenAI(api_key=settings.openai_api_key)

# Cache for embeddings (max 500 entries)
_embedding_cache: dict[str, list[float]] = {}
_EMBEDDING_CACHE_MAX = 500


async def chat_completion(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
) -> str:
    response = await _client.chat.completions.create(
        model=model or settings.openai_model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


async def chat_completion_stream(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
) -> AsyncIterator[str]:
    """Stream chat completion tokens as they arrive."""
    stream = await _client.chat.completions.create(
        model=model or settings.openai_model,
        messages=messages,
        temperature=temperature,
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


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


async def text_to_speech(text: str) -> bytes:
    """Convert text to speech using OpenAI TTS."""
    response = await _client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text,
    )
    return response.content
