"""Vector store wrapper over ChromaDB (local, persistent, no server).

Embeddings are pluggable via RAG_EMBED_BACKEND:
  - 'default' : Chroma's built-in ONNX MiniLM (all-MiniLM-L6-v2). No API key,
                runs offline after a one-time ~80MB model download.
  - 'openai'  : OpenAI text-embedding-3-small (needs OPENAI_API_KEY).

The store persists to RAG_STORE_DIR so ingested docs survive restarts.
"""
from __future__ import annotations

import os
from typing import Any

from . import cache, config

_CLIENT_TTL = 3600.0  # reuse the client/collection handle within a process


def _embedding_function():
    from chromadb.utils import embedding_functions as ef
    if config.EMBED_BACKEND == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("RAG_EMBED_BACKEND=openai but OPENAI_API_KEY is not set")
        return ef.OpenAIEmbeddingFunction(api_key=key, model_name="text-embedding-3-small")
    # default: local ONNX MiniLM — no key required
    return ef.DefaultEmbeddingFunction()


def _collection():
    import chromadb
    config.STORE_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(config.STORE_DIR))
    return client.get_or_create_collection(
        name=config.COLLECTION,
        embedding_function=_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )


def collection():
    """Cached collection handle (cosine space)."""
    return cache.get_or_fetch("chroma:collection", _CLIENT_TTL, _collection)


def upsert(ids: list[str], documents: list[str], metadatas: list[dict[str, Any]]) -> None:
    """Idempotent add: re-ingesting the same file overwrites instead of duplicating."""
    if not ids:
        return
    collection().upsert(ids=ids, documents=documents, metadatas=metadatas)


def query(text: str, k: int) -> list[dict[str, Any]]:
    """Return up to k passages: [{text, metadata, relevance}] sorted by relevance."""
    col = collection()
    n = min(k, max(1, col.count()))
    if n == 0:
        return []
    res = col.query(query_texts=[text], n_results=n,
                    include=["documents", "metadatas", "distances"])
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]
    out = []
    for doc, meta, dist in zip(docs, metas, dists):
        # cosine distance in [0,2]; map to a 0..1 relevance for display
        relevance = max(0.0, 1.0 - (dist / 2.0))
        out.append({"text": doc, "metadata": meta or {}, "relevance": relevance})
    return out


def count() -> int:
    try:
        return collection().count()
    except Exception:
        return 0


def reset() -> None:
    """Delete the collection (used by tests / re-index)."""
    import chromadb
    client = chromadb.PersistentClient(path=str(config.STORE_DIR))
    try:
        client.delete_collection(config.COLLECTION)
    except Exception:
        pass
    cache.clear()
