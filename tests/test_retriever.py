"""
Tests for HybridRetriever — #105 / #106 / #107

Uses an in-memory Chroma instance with fake (random) embeddings so that
no real API keys are needed.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.core.retriever import HybridRetriever, _rrf_merge, _tokenize


# ── Tokenizer ─────────────────────────────────────────────────────────────────

def test_tokenize_ascii():
    tokens = _tokenize("hello world")
    assert "hello" in tokens
    assert "world" in tokens


def test_tokenize_japanese():
    tokens = _tokenize("社内ドキュメント")
    # Should produce bigrams
    assert "社内" in tokens


def test_tokenize_empty():
    assert _tokenize("") == []


# ── RRF merge ─────────────────────────────────────────────────────────────────

def _make_item(doc_id: str, page: int, chunk: int = 0) -> dict:
    return {
        "text": f"content {doc_id} p{page}",
        "metadata": {"doc_id": doc_id, "filename": "f.txt", "page": page, "chunk_index": chunk},
        "score": 0.5,
    }


def test_rrf_merge_deduplicates():
    items = [_make_item("d1", 1), _make_item("d1", 2)]
    merged = _rrf_merge(items, items, top_k=10)
    uids = [
        f"{m['metadata']['doc_id']}{m['metadata']['page']}{m['metadata']['chunk_index']}"
        for m in merged
    ]
    assert len(uids) == len(set(uids))


def test_rrf_merge_respects_top_k():
    vector = [_make_item("d1", i) for i in range(10)]
    bm25 = [_make_item("d1", i) for i in range(10)]
    merged = _rrf_merge(vector, bm25, top_k=3)
    assert len(merged) <= 3


def test_rrf_merge_combines_lists():
    vector = [_make_item("d1", 1), _make_item("d2", 1)]
    bm25 = [_make_item("d3", 1), _make_item("d1", 1)]
    merged = _rrf_merge(vector, bm25, top_k=10)
    doc_ids = {m["metadata"]["doc_id"] for m in merged}
    assert "d1" in doc_ids
    assert "d3" in doc_ids


def test_rrf_score_attached():
    items = [_make_item("d1", 1)]
    merged = _rrf_merge(items, items, top_k=5)
    assert "score" in merged[0]
    assert isinstance(merged[0]["score"], float)


# ── HybridRetriever (mocked VectorStore) ─────────────────────────────────────

def _make_vs_mock(hits: list[dict]) -> MagicMock:
    vs = MagicMock()
    vs.similarity_search.return_value = hits
    return vs


def test_retriever_returns_results():
    hits = [_make_item("d1", i) for i in range(1, 4)]
    retriever = HybridRetriever(_make_vs_mock(hits))
    results = retriever.retrieve("社内マニュアルについて", top_k=3)
    assert len(results) <= 3


def test_retriever_empty_vectorstore():
    retriever = HybridRetriever(_make_vs_mock([]))
    results = retriever.retrieve("test query")
    assert results == []


def test_retriever_result_has_required_fields():
    hits = [_make_item("d1", 1, 0)]
    retriever = HybridRetriever(_make_vs_mock(hits))
    results = retriever.retrieve("query", top_k=5)
    assert len(results) >= 1
    item = results[0]
    assert "text" in item
    assert "metadata" in item
    assert "score" in item


def test_retriever_passes_category_filter():
    vs = _make_vs_mock([_make_item("d1", 1)])
    retriever = HybridRetriever(vs)
    retriever.retrieve("query", category="hr")
    vs.similarity_search.assert_called_once()
    call_kwargs = vs.similarity_search.call_args.kwargs
    assert call_kwargs.get("where") == {"category": "hr"}
