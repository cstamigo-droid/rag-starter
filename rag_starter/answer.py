"""Optional answer synthesis (cabled-but-optional, like a broker key).

With ANTHROPIC_API_KEY set, `answer()` returns a natural-language answer grounded
strictly in the retrieved passages, with inline [citation] tags. Without a key it
degrades gracefully to returning the ranked passages so the host LLM can answer —
the RAG still works, it just doesn't synthesize server-side.
"""
from __future__ import annotations

import os

from . import config
from .result import Result
from .retrieve import build_context, retrieve

_SYSTEM = (
    "You answer strictly from the provided document passages. Cite the passage "
    "tag like [source#0] or [file.pdf p3] inline after each claim. If the answer "
    "is not contained in the passages, say exactly: 'Not found in the documents.' "
    "Do not use outside knowledge. Be concise."
)


def answer(query: str, k: int | None = None) -> Result:
    """Retrieve, then (if a key is present) synthesize a cited answer."""
    r = retrieve(query, k)
    if not r.ok:
        return r
    passages = r.data["passages"]

    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        r.summary = ("No ANTHROPIC_API_KEY set — returning passages for the host LLM to "
                     "answer (cite the [tag] of each passage used).")
        return r

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        prompt = (
            f"Question: {query}\n\n"
            f"Passages:\n{build_context(passages)}\n\n"
            "Answer the question using only the passages above, with inline citations."
        )
        msg = client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=1024,
            system=_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(getattr(b, "text", "") for b in msg.content).strip()
        return Result(
            source="answer", ok=True,
            summary=text.split("\n", 1)[0][:160],
            data={"query": query, "answer": text, "passages": passages},
        )
    except Exception as e:
        r.summary = f"answer synthesis unavailable ({e}); returning passages instead."
        return r
