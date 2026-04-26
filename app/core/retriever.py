"""
HybridRetriever: combines vector search and BM25 keyword search
using Reciprocal Rank Fusion (RRF).

RRF score = Σ 1 / (k + rank_i)   where k=60 (standard constant)
"""

from __future__ import annotations

from typing import Any

from rank_bm25 import BM25Okapi

from app.core.config import settings
from app.core.vectorstore import VectorStoreManager


def _tokenize(text: str) -> list[str]:
    """
    Simple character-level bigram tokenizer that works for both
    Japanese (no spaces) and ASCII text.
    Also includes whole words split on whitespace for ASCII recall.
    """
    tokens = text.lower().split()
    # add character bigrams for CJK coverage
    for i in range(len(text) - 1):
        tokens.append(text[i : i + 2])
    return tokens


def _rrf_merge(
    vector_results: list[dict[str, Any]],
    bm25_results: list[dict[str, Any]],
    k: int = 60,
    top_k: int | None = None,
) -> list[dict[str, Any]]:
    """Merge two ranked lists with RRF and return deduplicated top-k."""
    scores: dict[str, float] = {}
    items: dict[str, dict[str, Any]] = {}

    for rank, item in enumerate(vector_results, start=1):
        uid = item["metadata"]["doc_id"] + str(item["metadata"]["page"]) + str(item["metadata"].get("chunk_index", 0))
        scores[uid] = scores.get(uid, 0.0) + 1.0 / (k + rank)
        items[uid] = item

    for rank, item in enumerate(bm25_results, start=1):
        uid = item["metadata"]["doc_id"] + str(item["metadata"]["page"]) + str(item["metadata"].get("chunk_index", 0))
        scores[uid] = scores.get(uid, 0.0) + 1.0 / (k + rank)
        items[uid] = item

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    limit = top_k or settings.top_k
    return [
        {**items[uid], "score": score}
        for uid, score in ranked[:limit]
    ]


class HybridRetriever:
    """
    Performs hybrid retrieval:
      1. Vector search via VectorStoreManager
      2. BM25 over the same candidate pool
      3. RRF fusion
    """

    def __init__(self, vector_store: VectorStoreManager) -> None:
        self._vs = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        k = top_k or settings.top_k
        # Fetch more candidates for BM25 to re-rank
        candidate_k = k * 4

        where = {"category": category} if category else None

        # 1. Vector search
        vector_hits = self._vs.similarity_search(query, k=candidate_k, where=where)

        if not vector_hits:
            return []

        # 2. BM25 over the vector candidate pool
        corpus = [_tokenize(h["text"]) for h in vector_hits]
        bm25 = BM25Okapi(corpus)
        query_tokens = _tokenize(query)
        bm25_scores = bm25.get_scores(query_tokens)

        bm25_hits = sorted(
            zip(bm25_scores, vector_hits),
            key=lambda x: x[0],
            reverse=True,
        )
        bm25_ranked = [item for _, item in bm25_hits]

        # 3. RRF merge
        return _rrf_merge(vector_hits, bm25_ranked, top_k=k)
