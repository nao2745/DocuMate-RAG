"""Tests for app.core.loader — #101 / #102"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.loader import (
    SUPPORTED_EXTENSIONS,
    load_document,
    load_markdown,
    load_txt,
)

DOC_ID = "test-doc-001"


# ── TXT ───────────────────────────────────────────────────────────────────────

def test_load_txt_returns_pages(txt_file: Path):
    pages = load_txt(txt_file, doc_id=DOC_ID)
    assert len(pages) >= 1


def test_load_txt_metadata(txt_file: Path):
    pages = load_txt(txt_file, doc_id=DOC_ID, category="manual")
    for page in pages:
        assert page["metadata"]["doc_id"] == DOC_ID
        assert page["metadata"]["filename"] == txt_file.name
        assert page["metadata"]["category"] == "manual"
        assert isinstance(page["metadata"]["page"], int)
        assert page["metadata"]["page"] >= 1


def test_load_txt_text_nonempty(txt_file: Path):
    pages = load_txt(txt_file, doc_id=DOC_ID)
    for page in pages:
        assert page["text"].strip() != ""


# ── Markdown ──────────────────────────────────────────────────────────────────

def test_load_markdown_splits_on_headers(md_file: Path):
    pages = load_markdown(md_file, doc_id=DOC_ID)
    # The fixture has 3 headings → expect at least 2 sections
    assert len(pages) >= 2


def test_load_markdown_metadata(md_file: Path):
    pages = load_markdown(md_file, doc_id=DOC_ID)
    for page in pages:
        assert page["metadata"]["filename"] == md_file.name
        assert isinstance(page["metadata"]["page"], int)


# ── PDF ───────────────────────────────────────────────────────────────────────

def test_load_pdf_returns_pages(pdf_file: Path):
    from app.core.loader import load_pdf
    pages = load_pdf(pdf_file, doc_id=DOC_ID)
    assert len(pages) == 2  # fixture creates 2 pages


def test_load_pdf_page_numbers(pdf_file: Path):
    from app.core.loader import load_pdf
    pages = load_pdf(pdf_file, doc_id=DOC_ID)
    page_nums = [p["metadata"]["page"] for p in pages]
    assert page_nums == sorted(page_nums)
    assert page_nums[0] == 1


# ── DOCX ──────────────────────────────────────────────────────────────────────

def test_load_docx_returns_pages(docx_file: Path):
    from app.core.loader import load_docx
    pages = load_docx(docx_file, doc_id=DOC_ID)
    assert len(pages) >= 1


def test_load_docx_text_contains_content(docx_file: Path):
    from app.core.loader import load_docx
    pages = load_docx(docx_file, doc_id=DOC_ID)
    combined = " ".join(p["text"] for p in pages)
    assert "パラグラフ" in combined


# ── Dispatcher ────────────────────────────────────────────────────────────────

def test_load_document_dispatches_txt(txt_file: Path):
    pages = load_document(txt_file, doc_id=DOC_ID)
    assert len(pages) >= 1


def test_load_document_dispatches_md(md_file: Path):
    pages = load_document(md_file, doc_id=DOC_ID)
    assert len(pages) >= 1


def test_load_document_unsupported_raises(tmp_path: Path):
    bad = tmp_path / "file.csv"
    bad.write_text("a,b,c")
    with pytest.raises(ValueError, match="Unsupported"):
        load_document(bad, doc_id=DOC_ID)


def test_supported_extensions_set():
    assert ".pdf" in SUPPORTED_EXTENSIONS
    assert ".docx" in SUPPORTED_EXTENSIONS
    assert ".md" in SUPPORTED_EXTENSIONS
    assert ".txt" in SUPPORTED_EXTENSIONS
