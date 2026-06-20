# rag-starter — chat with your documents (RAG), with citations

A production-ready starter that turns a folder of documents into a **cited Q&A
service**. Drop in your PDFs / Markdown / text, ask questions, get answers grounded
in the source — every claim traceable to the exact passage it came from.

Exposed two ways from one codebase:
- **MCP server** — plug it into Claude Desktop / Claude Code / any MCP host and chat with your docs.
- **HTTP API** (FastAPI) — call it from any app.

> Built once, reskinned per client. Swap the `data/` folder, tweak `config.py`, ship.

## Why it's different
- **Keyless by default.** Embeddings run locally (ONNX MiniLM) — no API key, no per-query cost, runs offline. Demo it anywhere in seconds.
- **Citations, not hallucinations.** Retrieval returns ranked passages tagged `[source#chunk]` / `[file.pdf p3]`. A missing answer returns *"Not found in the documents"* — never a fabricated one.
- **Answer synthesis is optional.** With an `ANTHROPIC_API_KEY` it writes a cited answer for you; without one it returns passages for the host LLM to answer. Either way the RAG works.
- **Idempotent ingestion.** Re-ingesting a file updates it in place (no duplicates).

## Quickstart

```bash
pip install -r requirements.txt          # or: pip install -e .
PYTHONUTF8=1 python tests/test_smoke.py   # proves retrieval works on the sample docs
```

### As an HTTP API
```bash
rag-starter-api            # uvicorn on 127.0.0.1:8000
# then:
curl -X POST localhost:8000/ingest  -H "content-type: application/json" -d '{"path":"./data"}'
curl -X POST localhost:8000/search  -H "content-type: application/json" -d '{"query":"refund policy"}'
curl -X POST localhost:8000/answer  -H "content-type: application/json" -d '{"query":"how long is the refund window?"}'
```

### As an MCP server (Claude Desktop)
Add to `claude_desktop_config.json` → `mcpServers`:
```json
{
  "rag-starter": {
    "command": "python",
    "args": ["-m", "rag_starter"],
    "cwd": "C:/path/to/rag-starter"
  }
}
```
Restart Claude Desktop, then: *"Ingest the folder ./data"*, then *"What's the refund policy?"*

## Tools / endpoints
| MCP tool | HTTP | Purpose |
|----------|------|---------|
| `rag_ingest(path)` | `POST /ingest` | Index a file or folder (txt/md/pdf). |
| `rag_search(query, k)` | `POST /search` | Top-k cited passages (keyless). |
| `rag_answer(query, k)` | `POST /answer` | Cited answer (with key) or passages (without). |
| — | `GET /health` | Liveness + indexed-chunk count + embedding backend. |

## Configuration
Everything is in `config.py` (or env / `.env` — see `.env.example`): chunk size & overlap,
top-k, embedding backend (`default` local vs `openai`), and the answer model. A client
reskin is usually just: replace `data/`, set `RAG_COLLECTION`, re-ingest.

## Architecture
```
documents ──ingest.py──> chunks(+citations) ──store.py──> Chroma (local, persistent)
                                                              │
question ─────────────────retrieve.py──> top-k cited passages┤
                                                              ├─> rag_search  (host LLM answers)
                                                  answer.py ──┴─> rag_answer  (server synthesizes, optional)
```
Reuses the mcp-factory contract (`Result`, `formatting`, `cache`) so it composes with the
rest of the catalog.

## License
MIT.
