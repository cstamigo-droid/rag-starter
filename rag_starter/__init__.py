"""rag-starter — production-ready RAG ("chat with your docs") starter.

Ingest documents (txt/md/pdf) -> chunk -> embed -> local vector store (Chroma),
then retrieve with citations. Exposed two ways:
  - MCP server (FastMCP) so Claude Desktop / agents can query your docs.
  - FastAPI HTTP API for any app.

Keyless by default: embeddings run locally (ONNX MiniLM, no API key). Answer
synthesis is optional — with an Anthropic key it returns a cited answer; without
one it returns ranked chunks for the calling LLM to answer.
"""
__version__ = "0.1.0"
