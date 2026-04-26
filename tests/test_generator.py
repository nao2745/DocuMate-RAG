"""
Tests for AnswerGenerator — #108 / #109

All LLM calls are mocked; no real API keys required.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.core.generator import AnswerGenerator, SYSTEM_PROMPT, _build_context

# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_chunk(doc_id: str, page: int, text: str) -> dict:
    return {
        "text": text,
        "metadata": {
            "doc_id": doc_id,
            "filename": f"{doc_id}.pdf",
            "page": page,
            "chunk_index": 0,
            "category": "general",
        },
        "score": 0.1,
    }


CHUNKS = [
    _make_chunk("doc1", 1, "有給休暇は年間20日付与されます。"),
    _make_chunk("doc1", 2, "取得手続きはHRポータルから行ってください。"),
]


# ── _build_context ─────────────────────────────────────────────────────────────

def test_build_context_contains_filename():
    ctx = _build_context(CHUNKS)
    assert "doc1.pdf" in ctx


def test_build_context_contains_page():
    ctx = _build_context(CHUNKS)
    assert "1" in ctx
    assert "2" in ctx


def test_build_context_contains_text():
    ctx = _build_context(CHUNKS)
    assert "有給休暇" in ctx


def test_build_context_empty():
    ctx = _build_context([])
    assert ctx == ""


# ── AnswerGenerator.generate (mocked LLM) ────────────────────────────────────

def _mock_llm(answer: str) -> MagicMock:
    llm = MagicMock()
    response = MagicMock()
    response.content = answer
    llm.invoke.return_value = response
    return llm


@patch("app.core.generator._build_llm")
def test_generate_returns_string(mock_build):
    mock_build.return_value = _mock_llm("有給休暇は年間20日です。")
    gen = AnswerGenerator()
    answer = gen.generate("有給休暇は何日ですか？", CHUNKS)
    assert isinstance(answer, str)
    assert len(answer) > 0


@patch("app.core.generator._build_llm")
def test_generate_calls_llm_with_system_prompt(mock_build):
    mock_llm = _mock_llm("回答テスト")
    mock_build.return_value = mock_llm
    gen = AnswerGenerator()
    gen.generate("テスト", CHUNKS)
    mock_llm.invoke.assert_called_once()
    messages = mock_llm.invoke.call_args[0][0]
    # First message must be system prompt
    assert messages[0].content == SYSTEM_PROMPT


@patch("app.core.generator._build_llm")
def test_generate_includes_context_in_human_message(mock_build):
    mock_llm = _mock_llm("回答")
    mock_build.return_value = mock_llm
    gen = AnswerGenerator()
    gen.generate("有給休暇は？", CHUNKS)
    messages = mock_llm.invoke.call_args[0][0]
    human_content = messages[1].content
    assert "有給休暇" in human_content


# ── AnswerGenerator.stream (mocked LLM) ──────────────────────────────────────

@patch("app.core.generator._build_llm")
def test_stream_yields_tokens(mock_build):
    tokens = ["有給", "休暇", "は", "20日", "です。"]
    mock_llm = MagicMock()
    mock_llm.stream.return_value = [MagicMock(content=t) for t in tokens]
    mock_build.return_value = mock_llm

    gen = AnswerGenerator()
    result = list(gen.stream("有給休暇は？", CHUNKS))
    assert result == tokens


@patch("app.core.generator._build_llm")
def test_stream_empty_chunks(mock_build):
    mock_llm = MagicMock()
    mock_llm.stream.return_value = [MagicMock(content="情報が見つかりません")]
    mock_build.return_value = mock_llm

    gen = AnswerGenerator()
    result = list(gen.stream("質問", []))
    assert len(result) > 0
