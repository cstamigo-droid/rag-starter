"""Central configuration. All tunables live here so a client reskin is one file.

Env vars (all optional — sensible defaults):
  RAG_DATA_DIR        where source documents live (default ./data)
  RAG_STORE_DIR       where the Chroma vector store persists (default ./.chroma)
  RAG_COLLECTION      collection name (default 'docs')
  RAG_CHUNK_SIZE      chars per chunk (default 1000)
  RAG_CHUNK_OVERLAP   char overlap between chunks (default 150)
  RAG_TOP_K           passages returned per query (default 4)
  RAG_EMBED_BACKEND   'default' (local ONNX MiniLM, no key) | 'openai'
  OPENAI_API_KEY      required only if RAG_EMBED_BACKEND=openai
  ANTHROPIC_API_KEY   optional — enables synthesized cited answers (rag_answer)
  ANTHROPIC_MODEL     default 'claude-sonnet-4-6'
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR      = Path(os.getenv("RAG_DATA_DIR", ROOT / "data"))
STORE_DIR     = Path(os.getenv("RAG_STORE_DIR", ROOT / ".chroma"))
COLLECTION    = os.getenv("RAG_COLLECTION", "docs")
CHUNK_SIZE    = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "150"))
TOP_K         = int(os.getenv("RAG_TOP_K", "4"))
EMBED_BACKEND = os.getenv("RAG_EMBED_BACKEND", "default").lower()

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

SUPPORTED_EXT = {".txt", ".md", ".markdown", ".pdf"}
