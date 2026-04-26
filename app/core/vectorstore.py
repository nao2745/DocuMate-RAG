"""
VectorStore: wraps Chroma + OpenAI embeddings.

Responsibilities:
  - add_chunks()     persist chunk-dicts to Chroma
  - delete_doc()     remove all chunks for a doc_id
  - similarity_search()  k-NN vector search
  - list_doc_ids()   return all stored doc_ids
"""

from __future__ import annotations

from typing import Any

import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings

COLLECTION_NAME = "documate"


def _embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
    )


class VectorStoreManager:
    def __init__(self, persist_directory: str | None = None) -> None:
        directory = persist_directory or str(settings.chroma_dir)
        self._client = chromadb.PersistentClient(path=directory)
        self._store = Chroma(
            client=self._client,
            collection_name=COLLECTION_NAME,
            embedding_function=_embeddings(),
        )

    # ── write ──────────────────────────────────────────────────────────────

    def add_chunks(self, chunks: list[dict[str, Any]]) -> None:
        """Embed and persist a list of chunk-dicts."""
        if not chunks:
            return
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        ids = [
            f"{m['doc_id']}_p{m['page']}_c{m['chunk_index']}"
            for m in metadatas
        ]
        self._store.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    def delete_doc(self, doc_id: str) -> int:
        """Delete all chunks belonging to doc_id. Returns deleted count."""
        collection = self._client.get_collection(COLLECTION_NAME)
        results = collection.get(where={"doc_id": doc_id})
        ids = results.get("ids", [])
        if ids:
            collection.delete(ids=ids)
        return len(ids)

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
        Score is cosine distance (lower = more similar).
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
        """Return distinct doc_ids stored in the collection."""
        try:
            collection = self._client.get_collection(COLLECTION_NAME)
            results = collection.get(include=["metadatas"])
            seen: set[str] = set()
            for meta in results.get("metadatas") or []:
                if meta and "doc_id" in meta:
                    seen.add(meta["doc_id"])
            return sorted(seen)
        except Exception:
            return []
