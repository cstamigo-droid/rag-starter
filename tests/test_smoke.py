"""Smoke test / eval — proves the RAG actually retrieves the right source.

Run directly:  PYTHONUTF8=1 python tests/test_smoke.py
Or with pytest: pytest -q

It ingests the sample docs into a TEMP store, runs a few questions, and asserts
the expected source document is cited in the top passages. 0 fabricated data:
if retrieval misses, the test fails loudly.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# isolate the store so the test never touches a real index
os.environ["RAG_STORE_DIR"] = tempfile.mkdtemp(prefix="rag_test_")
os.environ.setdefault("RAG_CHUNK_SIZE", "600")
os.environ.setdefault("RAG_CHUNK_OVERLAP", "100")

from rag_starter import ingest, retrieve, store  # noqa: E402

# (question, substring expected somewhere in the top passages, expected source file)
CASES = [
    ("How long do I have to get a refund?", "14 days", "policies.md"),
    ("How do I reset my password?", "Forgot password", "handbook.md"),
    ("What uptime does the Business plan guarantee?", "99.9", "policies.md"),
    ("How many concurrent workers does Pro include?", "5 concurrent", "handbook.md"),
]


def run() -> int:
    store.reset()
    res = ingest.ingest_path(str(ROOT / "data"))
    assert res.ok, f"ingest failed: {res.error}"
    print(f"[ingest] {res.summary}")

    failures = 0
    for q, needle, want_src in CASES:
        r = retrieve.retrieve(q, k=4)
        if not r.ok:
            print(f"FAIL  q={q!r}  -> retrieve error: {r.error}")
            failures += 1
            continue
        passages = r.data["passages"]
        joined = " ".join(p["text"] for p in passages)
        sources = {p["source"] for p in passages}
        ok = needle.lower() in joined.lower() and want_src in sources
        flag = "OK  " if ok else "FAIL"
        if not ok:
            failures += 1
        top = passages[0]
        print(f"{flag} q={q!r}\n      top=[{top['citation']}] rel={top['relevance']:.0%}  "
              f"needle_found={needle.lower() in joined.lower()}  src_found={want_src in sources}")

    print(f"\n{'ALL PASS' if failures == 0 else f'{failures} FAILED'} "
          f"({len(CASES)-failures}/{len(CASES)})")
    return failures


def test_smoke():
    assert run() == 0


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
