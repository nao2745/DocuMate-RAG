"""
Text chunker: splits loaded page-dicts into smaller overlapping chunks
suitable for embedding (500–1 000 tokens ≈ 800 chars default).
"""

from __future__ import annotations

from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


class TextChunker:
    """
    Wraps LangChain's RecursiveCharacterTextSplitter to produce
    chunk-dicts that carry all original metadata plus a chunk index.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size or settings.chunk_size,
            chunk_overlap=chunk_overlap or settings.chunk_overlap,
            separators=["\n\n", "\n", "。", "、", " ", ""],
            length_function=len,
        )

    def split(self, pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Split a list of page-dicts into chunk-dicts.

        Each output dict has the same shape as an input page-dict but adds:
          metadata.chunk_index  – 0-based index within the page
        """
        chunks: list[dict[str, Any]] = []
        for page in pages:
            text = page["text"]
            meta = page["metadata"]
            texts = self._splitter.split_text(text)
            for i, chunk_text in enumerate(texts):
                chunks.append({
                    "text": chunk_text,
                    "metadata": {**meta, "chunk_index": i},
                })
        return chunks
