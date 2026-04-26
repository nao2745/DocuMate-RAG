"""
Document loaders for PDF, DOCX, Markdown, and plain text files.

Each loader returns a list of dicts:
  {
    "text":     str,           # page / section content
    "metadata": {
        "doc_id":   str,
        "filename": str,
        "page":     int,       # 1-based
        "category": str,
    }
  }
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


# ── helpers ──────────────────────────────────────────────────────────────────

def _clean(text: str) -> str:
    """Collapse whitespace runs while preserving newlines."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ── loaders ──────────────────────────────────────────────────────────────────

def load_pdf(path: Path, doc_id: str, category: str = "general") -> list[dict[str, Any]]:
    """Load a PDF and return one item per page."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError("pypdf is required: pip install pypdf") from exc

    reader = PdfReader(str(path))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = _clean(page.extract_text() or "")
        if not text:
            continue
        pages.append({
            "text": text,
            "metadata": {
                "doc_id": doc_id,
                "filename": path.name,
                "page": i,
                "category": category,
            },
        })
    return pages


def load_docx(path: Path, doc_id: str, category: str = "general") -> list[dict[str, Any]]:
    """Load a Word document and return paragraphs grouped into pages (~50 paras each)."""
    try:
        from docx import Document
    except ImportError as exc:
        raise ImportError("python-docx is required: pip install python-docx") from exc

    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

    page_size = 50
    pages = []
    for page_num, start in enumerate(range(0, max(len(paragraphs), 1), page_size), start=1):
        chunk = paragraphs[start : start + page_size]
        text = _clean("\n".join(chunk))
        if not text:
            continue
        pages.append({
            "text": text,
            "metadata": {
                "doc_id": doc_id,
                "filename": path.name,
                "page": page_num,
                "category": category,
            },
        })
    return pages


def load_markdown(path: Path, doc_id: str, category: str = "general") -> list[dict[str, Any]]:
    """Load a Markdown file and split on H1/H2 headers as logical pages."""
    raw = path.read_text(encoding="utf-8")
    sections = re.split(r"(?m)^#{1,2} ", raw)
    pages = []
    for i, section in enumerate(sections, start=1):
        text = _clean(section)
        if not text:
            continue
        pages.append({
            "text": text,
            "metadata": {
                "doc_id": doc_id,
                "filename": path.name,
                "page": i,
                "category": category,
            },
        })
    return pages


def load_txt(path: Path, doc_id: str, category: str = "general") -> list[dict[str, Any]]:
    """Load a plain-text file; treat every 100 lines as one page."""
    lines = path.read_text(encoding="utf-8").splitlines()
    page_size = 100
    pages = []
    for page_num, start in enumerate(range(0, max(len(lines), 1), page_size), start=1):
        text = _clean("\n".join(lines[start : start + page_size]))
        if not text:
            continue
        pages.append({
            "text": text,
            "metadata": {
                "doc_id": doc_id,
                "filename": path.name,
                "page": page_num,
                "category": category,
            },
        })
    return pages


# ── dispatcher ───────────────────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".md", ".txt"}


def load_document(
    path: Path,
    doc_id: str,
    category: str = "general",
) -> list[dict[str, Any]]:
    """Dispatch to the appropriate loader based on file extension."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(path, doc_id, category)
    elif suffix == ".docx":
        return load_docx(path, doc_id, category)
    elif suffix == ".md":
        return load_markdown(path, doc_id, category)
    elif suffix == ".txt":
        return load_txt(path, doc_id, category)
    else:
        raise ValueError(
            f"Unsupported file type: '{suffix}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )
