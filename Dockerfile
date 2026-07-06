# rag-starter — MCP server (stdio transport). RAG keyless sobre ChromaDB.
# Cumple el requisito de Glama: la imagen arranca el server y responde a introspección.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt pyproject.toml README.md ./
COPY rag_starter ./rag_starter

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --no-deps .

# Directorio del vector store (persistencia local; se puede montar en runtime).
ENV RAG_STORE_DIR=/data
RUN mkdir -p /data

# El server MCP habla por stdio (Claude Desktop / Claude Code / introspección de Glama).
ENTRYPOINT ["rag-starter"]
