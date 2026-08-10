"""Pinecone vector store, wrapped for LangChain so the same object serves
both the ingestion upsert path (step 4) and the explainer's retriever
(step 5).
"""

from __future__ import annotations

from functools import lru_cache

from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from config import get_settings
from core.embeddings import EMBEDDING_DIMENSION, get_embeddings


@lru_cache
def _pinecone_client() -> Pinecone:
    settings = get_settings()
    return Pinecone(api_key=settings.pinecone_api_key)


def ensure_index_exists() -> None:
    """Create the transcript index if it doesn't exist yet. Safe to call
    repeatedly (e.g. at the start of an ingestion run) - a no-op if the
    index is already there.
    """
    settings = get_settings()
    client = _pinecone_client()
    existing = {index.name for index in client.list_indexes()}
    if settings.pinecone_index_name in existing:
        return
    client.create_index(
        name=settings.pinecone_index_name,
        dimension=EMBEDDING_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(cloud=settings.pinecone_cloud, region=settings.pinecone_region),
    )


@lru_cache
def get_vector_store() -> PineconeVectorStore:
    settings = get_settings()
    index = _pinecone_client().Index(settings.pinecone_index_name)
    return PineconeVectorStore(index=index, embedding=get_embeddings())
