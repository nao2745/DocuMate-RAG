"""
Document management endpoints (Vercel-ready).

POST   /api/documents/upload   – upload and ingest a document
GET    /api/documents           – list all documents
DELETE /api/documents/{doc_id}  – delete a document
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.core.loader import SUPPORTED_EXTENSIONS
from app.core.pipeline import IngestPipeline
from app.models.schemas import DeleteResponse, DocumentListResponse, DocumentMeta

router = APIRouter(prefix="/api/documents", tags=["documents"])
_pipeline = IngestPipeline()


@router.post("/upload", response_model=DocumentMeta)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(default="general"),
) -> DocumentMeta:
    """Upload and ingest a document (Vercel-friendly with tmp cleanup)."""
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"対応していないファイル形式です: {suffix}。"
                   f"対応形式: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    # Use temp directory for ephemeral filesystems (Vercel)
    temp_dir = Path(tempfile.gettempdir())
    dest = temp_dir / file.filename  # type: ignore[arg-type]

    try:
        # Write uploaded file to temp
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        # Check file size
        size_mb = dest.stat().st_size / (1024 * 1024)
        if size_mb > settings.max_file_size_mb:
            raise HTTPException(
                status_code=413,
                detail=f"ファイルサイズが上限（{settings.max_file_size_mb} MB）を超えています。",
            )

        # Ingest from temp file
        meta = _pipeline.ingest(dest, category=category)
        return meta

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"取り込みに失敗しました: {exc}") from exc
    finally:
        # Clean up temp file
        try:
            dest.unlink(missing_ok=True)
        except Exception:
            pass


@router.get("", response_model=DocumentListResponse)
async def list_documents() -> DocumentListResponse:
    docs = IngestPipeline.list_documents()
    return DocumentListResponse(documents=docs, total=len(docs))


@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete_document(doc_id: str) -> DeleteResponse:
    deleted = _pipeline.delete(doc_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="ドキュメントが見つかりません。")
    return DeleteResponse(doc_id=doc_id, message=f"{deleted} チャンクを削除しました。")
