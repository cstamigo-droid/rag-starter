# Publicación en Glama + awesome-mcp-servers — rag-starter
> Proceso 2026: **1 server por PR** + **registro en Glama**.

## ✅ Estado (hecho + verificado 2026-07-06)
- **Dockerfile** (`./Dockerfile`, Python 3.11-slim, stdio, ChromaDB) · **build OK** · **introspección VERIFICADA: 3 tools**
  (`rag_ingest`, `rag_search`, `rag_answer`).
- `glama.json` ya existe (maintainer `cstamigo-droid`). → Cumple el requisito de Glama.
- Nota: el vector store persiste en `RAG_STORE_DIR=/data` (montable en runtime).

## 🙋 Cristian
1. Registrar en https://glama.ai/mcp/servers → `github.com/cstamigo-droid/rag-starter` → anotar ruta Glama.
2. Abrir UN PR a `awesome-mcp-servers`.

## 📝 PR
**Título:** `Add rag-starter (keyless local RAG — chat with your docs)`
**Entrada README:**
```
- [cstamigo-droid/rag-starter](https://github.com/cstamigo-droid/rag-starter) 🐍 🏠 - Keyless local RAG over MCP: ingest your documents into ChromaDB, semantic search, and grounded answers — 3 tools. Chat with your own docs, no API keys.
```
**Badge** (reemplazar `<GLAMA_PATH>`):
```
[![rag-starter MCP server](https://glama.ai/mcp/servers/<GLAMA_PATH>/badges/score.svg)](https://glama.ai/mcp/servers/<GLAMA_PATH>)
```
