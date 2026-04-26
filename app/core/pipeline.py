"""
High-level pipelines used by the API layer (Vercel-ready).

IngestPipeline  – file → chunks → vector DB
QueryPipeline   – question → retrieve → generate → sources
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Generator

from app.core.chunker import TextChunker
from app.core.config import settings
from app.core.generator import AnswerGenerator
from app.core.loader import load_document
from app.core.retriever import HybridRetriever
from app.core.vectorstore import VectorStoreManager
from app.models.schemas import ChatResponse, DocumentMeta, Source

# In-memory registry cache (Vercel-friendly, no persistent file needed)
_REGISTRY_CACHE: dict[str, Any] = {}


def _load_registry() -> dict[str, Any]:
    """Load registry from cache or file if present."""
    global _REGISTRY_CACHE
    if not _REGISTRY_CACHE:
        registry_path = Path("data/document_registry.json")
        if registry_path.exists():
            try:
                _REGISTRY_CACHE = json.loads(
                    registry_path.read_text(encoding="utf-8")
                )
            except Exception:
                _REGISTRY_CACHE = {}
    return _REGISTRY_CACHE


def _save_registry(registry: dict[str, Any]) -> None:
    """Save registry to cache and optionally to file."""
    global _REGISTRY_CACHE
    _REGISTRY_CACHE = registry
    
    # Try to save to file (may fail on Vercel, but that's OK)
    try:
        registry_path = Path("data/document_registry.json")
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(
            json.dumps(registry, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
    except Exception:
        # Vercel or other read-only environments: silently skip file save
        pass


class IngestPipeline:
    def __init__(
        self,
        vector_store: VectorStoreManager | None = None,
        chunker: TextChunker | None = None,
    ) -> None:
        self._vs = vector_store or VectorStoreManager()
        self._chunker = chunker or TextChunker()

    def ingest(self, file_path: Path, category: str = "general") -> DocumentMeta:
        """
        Load → chunk → embed → store.
        Returns a DocumentMeta for the ingested document.
        """
        doc_id = str(uuid.uuid4())

        # 1. Load pages
        pages = load_document(file_path, doc_id=doc_id, category=category)

        # 2. Chunk
        chunks = self._chunker.split(pages)

        # 3. Embed + store
        self._vs.add_chunks(chunks)

        # 4. Build metadata
        meta = DocumentMeta(
            doc_id=doc_id,
            filename=file_path.name,
            file_type=file_path.suffix.lower().lstrip("."),
            size_bytes=file_path.stat().st_size,
            page_count=len(pages),
            category=category,
            uploaded_at=datetime.now(),
        )

        # 5. Persist registry
        registry = _load_registry()
        registry[doc_id] = meta.model_dump()
        _save_registry(registry)

        return meta

    def delete(self, doc_id: str) -> int:
        """Delete document from vector store and registry."""
        deleted = self._vs.delete_doc(doc_id)
        registry = _load_registry()
        registry.pop(doc_id, None)
        _save_registry(registry)
        return deleted

    @staticmethod
    def list_documents() -> list[DocumentMeta]:
        registry = _load_registry()
        return [DocumentMeta(**v) for v in registry.values()]


class QueryPipeline:
    def __init__(
        self,
        vector_store: VectorStoreManager | None = None,
        generator: AnswerGenerator | None = None,
    ) -> None:
        vs = vector_store or VectorStoreManager()
        self._retriever = HybridRetriever(vs)
        self._generator = generator or AnswerGenerator()

    def query(
        self,
        question: str,
        session_id: str | None = None,
        category: str | None = None,
    ) -> ChatResponse:
        """Retrieve → generate → return ChatResponse."""
        sid = session_id or str(uuid.uuid4())

        chunks = self._retriever.retrieve(question, category=category)

        if not chunks:
            return ChatResponse(
                answer="提供されたドキュメントにはその情報が見つかりませんでした。",
                sources=[],
                session_id=sid,
            )

        answer = self._generator.generate(question, chunks)

        sources = [
            Source(
                doc_id=c["metadata"]["doc_id"],
                filename=c["metadata"]["filename"],
                page=c["metadata"]["page"],
                score=float(c.get("score", 0.0)),
                excerpt=c["text"][:200],
            )
            for c in chunks
        ]

        return ChatResponse(answer=answer, sources=sources, session_id=sid)

    def stream(
        self,
        question: str,
        session_id: str | None = None,
        category: str | None = None,
    ) -> tuple[Generator[str, None, None], list[Source], str]:
        """
        Returns (token_generator, sources, session_id).
        The caller iterates the generator to get streaming tokens.
        """
        sid = session_id or str(uuid.uuid4())
        chunks = self._retriever.retrieve(question, category=category)

        sources = [
            Source(
                doc_id=c["metadata"]["doc_id"],
                filename=c["metadata"]["filename"],
                page=c["metadata"]["page"],
                score=float(c.get("score", 0.0)),
                excerpt=c["text"][:200],
            )
            for c in chunks
        ]

        if not chunks:
            def _empty():
                yield "提供されたドキュメントにはその情報が見つかりませんでした。"
            return _empty(), [], sid

        return self._generator.stream(question, chunks), sources, sid
