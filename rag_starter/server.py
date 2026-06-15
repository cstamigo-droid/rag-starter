#!/usr/bin/env python3
"""rag-starter — chat with your documents (RAG) over MCP.

Transport: stdio (local — Claude Desktop / Claude Code / agents).

Tools:
  rag_ingest(path)        index a file or folder of docs (txt/md/pdf)
  rag_search(query, k)    return the top-k cited passages (keyless; host answers)
  rag_answer(query, k)    synthesized cited answer if ANTHROPIC_API_KEY is set,
                          else falls back to passages

Everything is grounded: passages carry citations and a missing source returns an
honest "no data", never a fabricated answer.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

from . import answer as answer_mod
from . import config, ingest, retrieve
from .formatting import ResponseFormat, render

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

mcp = FastMCP("rag-starter")


async def _run(fn, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: fn(*args))


class IngestInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    path: str = Field(..., description="File or folder to index (txt/md/pdf).", min_length=1)
    response_format: ResponseFormat = ResponseFormat.MARKDOWN


class QueryInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    query: str = Field(..., description="The question to answer from the documents.",
                       min_length=1, max_length=1000)
    k: int = Field(default=config.TOP_K, ge=1, le=20,
                   description="How many passages to retrieve.")
    response_format: ResponseFormat = ResponseFormat.MARKDOWN


@mcp.tool(
    name="rag_ingest",
    annotations={"title": "Ingest Documents", "readOnlyHint": False,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def rag_ingest(params: IngestInput) -> str:
    """Index a document or folder so it can be searched and cited.

    Examples:
        - "Index the folder ./data" -> path='./data'
        - "Add the handbook pdf" -> path='docs/handbook.pdf'
    """
    result = await _run(ingest.ingest_path, params.path)
    return render(result, f"Ingest — {params.path}", params.response_format)


@mcp.tool(
    name="rag_search",
    annotations={"title": "Search Documents", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def rag_search(params: QueryInput) -> str:
    """Return the most relevant passages for a question, each with a citation.

    Use this to ground your own answer: read the passages and cite their [tags].

    Examples:
        - "What is the refund policy?" -> query='refund policy'
        - "How do I reset my password?" -> query='reset password'
    """
    result = await _run(retrieve.retrieve, params.query, params.k)
    return render(result, f"Search — {params.query}", params.response_format)


@mcp.tool(
    name="rag_answer",
    annotations={"title": "Answer From Documents", "readOnlyHint": True,
                 "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
)
async def rag_answer(params: QueryInput) -> str:
    """Answer a question grounded in the documents, with citations.

    With ANTHROPIC_API_KEY set, returns a synthesized cited answer; otherwise
    returns the ranked passages for you to answer from.

    Examples:
        - "Summarize the cancellation terms" -> query='cancellation terms'
        - "Does the plan include support?" -> query='support included in plan'
    """
    result = await _run(answer_mod.answer, params.query, params.k)
    return render(result, f"Answer — {params.query}", params.response_format)


def main() -> None:
    """Console entrypoint — runs the MCP server over stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
