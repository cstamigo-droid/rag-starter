"""Document ingestion: load (txt/md/pdf) -> chunk (with overlap) -> embed -> store.

Every chunk keeps its provenance (source file, page, chunk index) so retrieval
can cite exactly where an answer came from. Ingestion is idempotent: re-ingesting
the same file upserts by deterministic id instead of duplicating.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from . import config, store
from .result import Result


# ─── loading ──────────────────────────────────────────────────────────────────

def _load(path: Path) -> list[tuple[str, int | None]]:
    """Return [(text, page_or_None)] for one file."""
    ext = path.suffix.lower()
    if ext in {".txt", ".md", ".markdown"}:
        return [(path.read_text(encoding="utf-8", errors="replace"), None)]
    if ext == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        pages = []
        for i, pg in enumerate(reader.pages, start=1):
            txt = pg.extract_text() or ""
            if txt.strip():
                pages.append((txt, i))
        return pages
    raise ValueError(f"unsupported extension: {ext}")


# ─── chunking ───────────────────────────────────────────────────────────────--

def _hard_split(s: str, size: int, overlap: int) -> list[str]:
    step = max(1, size - overlap)
    return [s[i:i + size] for i in range(0, len(s), step)]


def chunk_text(text: str, size: int, overlap: int) -> list[str]:
    """Pack lines into ~`size`-char chunks with `overlap` char carryover.

    Breaks on line boundaries where possible; hard-splits any single line longer
    than `size` so no chunk exceeds the embedding model's comfort zone.
    """
    text = (text or "").replace("\r", "").strip()
    if not text:
        return []
    units: list[str] = []
    for line in (ln.strip() for ln in text.split("\n") if ln.strip()):
        units.extend(_hard_split(line, size, overlap) if len(line) > size else [line])

    chunks: list[str] = []
    cur = ""
    for u in units:
        if cur and len(cur) + len(u) + 1 > size:
            chunks.append(cur)
            tail = cur[-overlap:] if overlap and len(cur) > overlap else ""
            cur = f"{tail}\n{u}".strip() if tail else u
        else:
            cur = f"{cur}\n{u}" if cur else u
    if cur:
        chunks.append(cur)
    return chunks


# ─── ingestion ──────────────────────────────────────────────────────────────--

def _iter_files(target: Path) -> list[Path]:
    if target.is_dir():
        return sorted(p for p in target.rglob("*") if p.suffix.lower() in config.SUPPORTED_EXT)
    return [target] if target.suffix.lower() in config.SUPPORTED_EXT else []


def ingest_path(path: str) -> Result:
    """Ingest a file or a directory of files into the vector store."""
    target = Path(path).expanduser()
    if not target.exists():
        return Result.failed("ingest", f"path not found: {target}")
    files = _iter_files(target)
    if not files:
        return Result.failed("ingest", f"no supported docs ({', '.join(sorted(config.SUPPORTED_EXT))}) under {target}")

    ids: list[str] = []
    docs: list[str] = []
    metas: list[dict[str, Any]] = []
    n_files = 0
    for f in files:
        try:
            sections = _load(f)
        except Exception as e:
            continue
        n_files += 1
        src = f.name
        for text, page in sections:
            for ci, chunk in enumerate(chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)):
                pg = page if page is not None else 0
                ids.append(f"{src}:{pg}:{ci}")
                docs.append(chunk)
                citation = f"{src} p{page}" if page is not None else f"{src}#{ci}"
                metas.append({"source": src, "page": page if page is not None else -1,
                              "chunk": ci, "citation": citation})

    if not docs:
        return Result.failed("ingest", "no extractable text found")
    store.upsert(ids, docs, metas)
    return Result(
        source="ingest", ok=True,
        summary=f"Ingested {len(docs)} chunks from {n_files} file(s). Store now holds {store.count()} chunks.",
        data={"files": n_files, "chunks_added": len(docs), "store_total": store.count()},
    )
