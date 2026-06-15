"""FastAPI HTTP interface — the same RAG for any app (not just MCP hosts).

Run:  uvicorn rag_starter.api:app --reload    (or `rag-starter-api`)
Then: POST /ingest {"path": "./data"}
      POST /search {"query": "...", "k": 4}
      POST /answer {"query": "...", "k": 4}
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

from . import answer as answer_mod
from . import config, ingest, retrieve, store

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(title="rag-starter", version="0.1.0",
              description="Chat with your documents (RAG) with citations.")


class IngestBody(BaseModel):
    path: str = Field(..., description="File or folder to index.")


class QueryBody(BaseModel):
    query: str
    k: int = Field(default=config.TOP_K, ge=1, le=20)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "chunks_indexed": store.count(),
            "embed_backend": config.EMBED_BACKEND}


@app.post("/ingest")
def api_ingest(body: IngestBody) -> dict:
    return ingest.ingest_path(body.path).to_dict()


@app.post("/search")
def api_search(body: QueryBody) -> dict:
    return retrieve.retrieve(body.query, body.k).to_dict()


@app.post("/answer")
def api_answer(body: QueryBody) -> dict:
    return answer_mod.answer(body.query, body.k).to_dict()


def main() -> None:
    """Console entrypoint — runs the HTTP API."""
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
