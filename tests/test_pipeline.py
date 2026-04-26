"""
Integration tests for IngestPipeline + QueryPipeline — #006 / #110

All external services (vector DB embeddings, LLM) are mocked.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.core.chunker import TextChunker
from app.core.pipeline import IngestPipeline, QueryPipeline
from app.core.retriever import HybridRetriever


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _mock_vs(hits: list[dict] | None = None) -> MagicMock:
    vs = MagicMock()
    vs.add_chunks.return_value = None
    vs.delete_doc.return_value = 3
    vs.similarity_search.return_value = hits or []
    vs.list_doc_ids.return_value = []
    return vs


def _mock_generator(answer: str = "テスト回答です。") -> MagicMock:
    gen = MagicMock()
    gen.generate.return_value = answer
    return gen


# ── IngestPipeline ────────────────────────────────────────────────────────────

def test_ingest_txt_returns_meta(txt_file: Path, tmp_path: Path):
    vs = _mock_vs()
    with patch("app.core.pipeline._load_registry", return_value={}), \
         patch("app.core.pipeline._save_registry"):
        pipeline = IngestPipeline(vector_store=vs)
        meta = pipeline.ingest(txt_file, category="hr")

    assert meta.filename == txt_file.name
    assert meta.file_type == "txt"
    assert meta.category == "hr"
    assert meta.page_count >= 1
    assert meta.doc_id != ""


def test_ingest_calls_add_chunks(txt_file: Path):
    vs = _mock_vs()
    with patch("app.core.pipeline._load_registry", return_value={}), \
         patch("app.core.pipeline._save_registry"):
        pipeline = IngestPipeline(vector_store=vs)
        pipeline.ingest(txt_file)

    vs.add_chunks.assert_called_once()
    chunks = vs.add_chunks.call_args[0][0]
    assert len(chunks) >= 1


def test_ingest_md_returns_meta(md_file: Path):
    vs = _mock_vs()
    with patch("app.core.pipeline._load_registry", return_value={}), \
         patch("app.core.pipeline._save_registry"):
        pipeline = IngestPipeline(vector_store=vs)
        meta = pipeline.ingest(md_file)

    assert meta.file_type == "md"


def test_delete_calls_vs_delete():
    vs = _mock_vs()
    with patch("app.core.pipeline._load_registry", return_value={"abc": {}}), \
         patch("app.core.pipeline._save_registry"):
        pipeline = IngestPipeline(vector_store=vs)
        count = pipeline.delete("abc")

    vs.delete_doc.assert_called_once_with("abc")
    assert count == 3


# ── QueryPipeline ─────────────────────────────────────────────────────────────

def _hit(doc_id: str, page: int, text: str) -> dict:
    return {
        "text": text,
        "metadata": {
            "doc_id": doc_id,
            "filename": f"{doc_id}.pdf",
            "page": page,
            "chunk_index": 0,
            "category": "general",
        },
        "score": 0.2,
    }


def test_query_returns_chat_response():
    hits = [_hit("d1", 1, "有給休暇は20日です。")]
    vs = _mock_vs(hits)
    gen = _mock_generator("有給休暇は年間20日付与されます。")

    pipeline = QueryPipeline(vector_store=vs, generator=gen)
    resp = pipeline.query("有給休暇は何日ですか？")

    assert resp.answer == "有給休暇は年間20日付与されます。"
    assert len(resp.sources) == 1
    assert resp.sources[0].filename == "d1.pdf"
    assert resp.session_id != ""


def test_query_no_results_returns_fallback():
    vs = _mock_vs([])  # empty retrieval
    gen = _mock_generator()

    pipeline = QueryPipeline(vector_store=vs, generator=gen)
    resp = pipeline.query("存在しない情報")

    assert "見つかりません" in resp.answer
    assert resp.sources == []


def test_query_source_excerpt_truncated():
    long_text = "あ" * 500
    hits = [_hit("d1", 1, long_text)]
    vs = _mock_vs(hits)
    gen = _mock_generator("回答")

    pipeline = QueryPipeline(vector_store=vs, generator=gen)
    resp = pipeline.query("質問")

    assert len(resp.sources[0].excerpt) <= 200


def test_query_session_id_preserved():
    hits = [_hit("d1", 1, "content")]
    vs = _mock_vs(hits)
    gen = _mock_generator("回答")

    pipeline = QueryPipeline(vector_store=vs, generator=gen)
    resp = pipeline.query("質問", session_id="my-session-123")

    assert resp.session_id == "my-session-123"


def test_stream_returns_generator_and_sources():
    hits = [_hit("d1", 2, "内容")]
    vs = _mock_vs(hits)
    gen = MagicMock()
    gen.stream.return_value = iter(["回", "答"])

    pipeline = QueryPipeline(vector_store=vs, generator=gen)
    token_gen, sources, sid = pipeline.stream("質問")

    tokens = list(token_gen)
    assert tokens == ["回", "答"]
    assert len(sources) == 1
    assert sid != ""
