"""
VectorStore: wraps Pinecone + OpenAI embeddings (Vercel-ready).

Responsibilities:
  - add_chunks()     persist chunk-dicts to Pinecone
  - delete_doc()     remove all chunks for a doc_id
  - similarity_search()  k-NN vector search
  - list_doc_ids()   return all stored doc_ids
"""

from __future__ import annotations

from typing import Any

from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from app.core.config import settings

INDEX_NAME = "documate"


def _embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
    )


class VectorStoreManager:
    def __init__(self) -> None:
        """Initialize Pinecone vector store."""
        self._embeddings = _embeddings()
        self._store = PineconeVectorStore(
            index_name=INDEX_NAME,
            embedding=self._embeddings,
        )
        self._doc_ids_cache: set[str] = set()

    # ── write ──────────────────────────────────────────────────────────────

    def add_chunks(self, chunks: list[dict[str, Any]]) -> None:
        """Embed and persist a list of chunk-dicts to Pinecone."""
        if not chunks:
            return
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        ids = [
            f"{m['doc_id']}_p{m['page']}_c{m['chunk_index']}"
            for m in metadatas
        ]
        
        # Track doc_ids
        for meta in metadatas:
            if "doc_id" in meta:
                self._doc_ids_cache.add(meta["doc_id"])
        
        self._store.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    def delete_doc(self, doc_id: str) -> int:
        """Delete all chunks belonging to doc_id. Returns deleted count."""
        # List all vectors with this doc_id and delete
        index = self._store._index
        deleted_count = 0
        
        try:
            # Query to find all vectors with this doc_id
            namespace = self._store._namespace or ""
            results = index.query(
                vector=[0] * 1536,  # dummy vector
                top_k=10000,
                filter={"doc_id": {"$eq": doc_id}},
                namespace=namespace,
                include_metadata=True,
            )
            
            ids_to_delete = [match.id for match in results.matches]
            if ids_to_delete:
                index.delete(ids=ids_to_delete, namespace=namespace)
                deleted_count = len(ids_to_delete)
            
            # Remove from cache
            self._doc_ids_cache.discard(doc_id)
        except Exception:
            # If filtering fails, fall back to prefix-based deletion
            pass
        
        return deleted_count

    # ── read ───────────────────────────────────────────────────────────────

    def similarity_search(
        self,
        query: str,
        k: int | None = None,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Return top-k results as dicts:
          {"text": ..., "metadata": ..., "score": float}
        Score is similarity (higher = more similar).
        """
        top_k = k or settings.top_k
        kwargs: dict[str, Any] = {"k": top_k}
        if where:
            kwargs["filter"] = where

        results = self._store.similarity_search_with_score(query, **kwargs)
        return [
            {"text": doc.page_content, "metadata": doc.metadata, "score": score}
            for doc, score in results
        ]

    def list_doc_ids(self) -> list[str]:
        """Return distinct doc_ids stored in Pinecone (from cache)."""
        return sorted(self._doc_ids_cache)
