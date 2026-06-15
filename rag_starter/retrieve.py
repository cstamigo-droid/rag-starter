"""Retrieval: turn a question into the top-k cited passages from the store.

This is the keyless heart of the RAG: it returns ranked passages WITH citations.
The calling LLM (Claude in an MCP host, or your app) writes the answer grounded
in these passages. `answer.py` optionally does that synthesis server-side.
"""
from __future__ import annotations

from . import config, store
from .result import Result


def retrieve(query: str, k: int | None = None) -> Result:
    """Return the top-k passages most relevant to `query`, each with a citation."""
    q = (query or "").strip()
    if not q:
        return Result.failed("retrieve", "empty query")
    if store.count() == 0:
        return Result.failed("retrieve", "store is empty — ingest documents first")

    k = k or config.TOP_K
    hits = store.query(q, k)
    if not hits:
        return Result.failed("retrieve", "no relevant passages found")

    passages = []
    for h in hits:
        m = h["metadata"]
        passages.append({
            "text": h["text"],
            "source": m.get("source", "?"),
            "page": m.get("page", -1),
            "chunk": m.get("chunk", -1),
            "citation": m.get("citation", "?"),
            "relevance": round(h["relevance"], 3),
        })
    top = passages[0]
    return Result(
        source="retrieve", ok=True,
        summary=f"{len(passages)} passage(s) found. Best match: [{top['citation']}] (relevance {top['relevance']:.0%}).",
        data={"query": q, "passages": passages},
    )


def build_context(passages: list[dict]) -> str:
    """Format passages as a citation-tagged context block for an LLM prompt."""
    blocks = []
    for p in passages:
        blocks.append(f"[{p['citation']}]\n{p['text'].strip()}")
    return "\n\n".join(blocks)
