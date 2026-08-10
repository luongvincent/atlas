"""Embedding model.

Groq (this project's only configured LLM provider) doesn't serve embedding
models, and .env intentionally has no separate embeddings API key - so we
use a small local model via fastembed (ONNX runtime, CPU, no GPU/API key,
no network calls at inference time) instead of introducing an undeclared
dependency like OpenAI. bge-small-en-v1.5 is a well-established, free
384-dimension general text embedding model; that dimension must match the
Pinecone index created in core/vector_store.py.
"""

from __future__ import annotations

from functools import lru_cache

from langchain_community.embeddings import FastEmbedEmbeddings

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIMENSION = 384


@lru_cache
def get_embeddings() -> FastEmbedEmbeddings:
    return FastEmbedEmbeddings(model_name=EMBEDDING_MODEL_NAME)
