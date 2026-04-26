"""
Document management endpoints.

POST   /api/documents/upload   – upload and ingest a document
GET    /api/documents           – list all documents
DELETE /api/documents/{doc_id}  – delete a document
"""

from __future__ import annotations

import shutil
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
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"対応していないファイル形式です: {suffix}。"
                   f"対応形式: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    # Size check (read first chunk to estimate; full check after save)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    dest = settings.upload_dir / file.filename  # type: ignore[arg-type]

    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    size_mb = dest.stat().st_size / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=413,
            detail=f"ファイルサイズが上限（{settings.max_file_size_mb} MB）を超えています。",
        )

    try:
        meta = _pipeline.ingest(dest, category=category)
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"取り込みに失敗しました: {exc}") from exc

    return meta


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
