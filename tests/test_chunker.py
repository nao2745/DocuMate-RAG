"""Tests for app.core.chunker — #103"""

from __future__ import annotations

from app.core.chunker import TextChunker

DOC_ID = "chunk-test-001"

PAGES = [
    {
        "text": "これはテスト用の長いテキストです。" * 60,  # ~900 chars
        "metadata": {"doc_id": DOC_ID, "filename": "test.txt", "page": 1, "category": "general"},
    },
    {
        "text": "短いテキスト。",
        "metadata": {"doc_id": DOC_ID, "filename": "test.txt", "page": 2, "category": "general"},
    },
]


def test_chunker_produces_chunks():
    chunker = TextChunker(chunk_size=200, chunk_overlap=20)
    chunks = chunker.split(PAGES)
    assert len(chunks) > len(PAGES)


def test_chunker_preserves_metadata():
    chunker = TextChunker(chunk_size=200, chunk_overlap=20)
    chunks = chunker.split(PAGES)
    for chunk in chunks:
        assert chunk["metadata"]["doc_id"] == DOC_ID
        assert chunk["metadata"]["filename"] == "test.txt"
        assert "page" in chunk["metadata"]
        assert "chunk_index" in chunk["metadata"]


def test_chunker_chunk_index_starts_at_zero():
    chunker = TextChunker(chunk_size=200, chunk_overlap=20)
    chunks = chunker.split([PAGES[0]])
    indices = [c["metadata"]["chunk_index"] for c in chunks]
    assert indices[0] == 0
    assert indices == list(range(len(indices)))


def test_chunker_respects_chunk_size():
    chunker = TextChunker(chunk_size=100, chunk_overlap=10)
    chunks = chunker.split(PAGES)
    # Allow some slack for sentence boundaries
    for chunk in chunks:
        assert len(chunk["text"]) <= 150


def test_chunker_empty_pages():
    chunker = TextChunker()
    assert chunker.split([]) == []


def test_chunker_short_text_stays_single_chunk():
    chunker = TextChunker(chunk_size=800, chunk_overlap=100)
    chunks = chunker.split([PAGES[1]])
    assert len(chunks) == 1
    assert chunks[0]["text"] == PAGES[1]["text"]


def test_chunker_text_nonempty():
    chunker = TextChunker(chunk_size=200, chunk_overlap=20)
    chunks = chunker.split(PAGES)
    for chunk in chunks:
        assert chunk["text"].strip() != ""
