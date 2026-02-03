"""Retrieve relevant memories for a given context."""

import json
import logging
import sqlite3

import numpy as np
from openai import OpenAIError

from atlas.memory.store import get_all_memories, touch_memory, _get_conn
from atlas.services.openai_client import get_embedding, get_embeddings_batch

logger = logging.getLogger(__name__)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr = np.array(a)
    b_arr = np.array(b)
    dot = np.dot(a_arr, b_arr)
    norm = np.linalg.norm(a_arr) * np.linalg.norm(b_arr)
    if norm == 0:
        return 0.0
    return float(dot / norm)


async def retrieve_relevant_memories(query: str, k: int = 5) -> list[dict]:
    """Find the top-k most relevant memories for a query.

    Uses embedding similarity to rank memories.
    Falls back to recency if embeddings are unavailable.
    """
    memories = get_all_memories()
    if not memories:
        return []

    try:
        query_embedding = await get_embedding(query)
    except OpenAIError as e:
        logger.warning("OpenAI embedding failed, falling back to recency: %s", e)
        return [{"content": m["content"], "category": m["category"]} for m in memories[:k]]
    except Exception as e:
        logger.exception("Unexpected error getting embedding")
        return [{"content": m["content"], "category": m["category"]} for m in memories[:k]]

    # Separate memories with and without embeddings
    with_embedding = []
    without_embedding = []

    for mem in memories:
        emb_json = mem.get("embedding")
        if emb_json:
            try:
                mem_embedding = json.loads(emb_json)
                with_embedding.append((mem, mem_embedding))
            except json.JSONDecodeError:
                without_embedding.append(mem)
        else:
            without_embedding.append(mem)

    # Batch compute missing embeddings
    if without_embedding:
        try:
            texts = [m["content"] for m in without_embedding]
            new_embeddings = await get_embeddings_batch(texts)

            # Update database in batch
            conn = _get_conn()
            for mem, emb in zip(without_embedding, new_embeddings):
                conn.execute(
                    "UPDATE memories SET embedding = ? WHERE id = ?",
                    (json.dumps(emb), mem["id"]),
                )
                with_embedding.append((mem, emb))
            conn.commit()
        except OpenAIError as e:
            logger.warning("OpenAI batch embedding failed: %s", e)
        except sqlite3.Error as e:
            logger.error("Database error saving embeddings: %s", e)
        except Exception as e:
            logger.exception("Unexpected error in batch embedding")

    # Score all memories
    scored = []
    for mem, mem_embedding in with_embedding:
        sim = _cosine_similarity(query_embedding, mem_embedding)
        scored.append((sim, mem))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for sim, mem in scored[:k]:
        if sim > 0.3:
            touch_memory(mem["id"])
            results.append({
                "content": mem["content"],
                "category": mem["category"],
                "confidence": mem["confidence"],
            })

    return results
