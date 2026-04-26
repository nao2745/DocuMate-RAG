"""
Chat endpoints.

POST /api/chat/query    – question → answer + sources (blocking)
POST /api/chat/feedback – submit helpful/unhelpful rating
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.pipeline import QueryPipeline
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
    FeedbackResponse,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])
_pipeline = QueryPipeline()

_FEEDBACK_PATH = Path("data/feedback.jsonl")


@router.post("/query", response_model=ChatResponse)
async def query(req: ChatRequest) -> ChatResponse:
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="質問が空です。")
    if len(req.question) > 2000:
        raise HTTPException(status_code=400, detail="質問は2,000文字以内にしてください。")

    try:
        return _pipeline.query(
            question=req.question,
            session_id=req.session_id,
            category=req.category,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"回答生成に失敗しました: {exc}") from exc


@router.post("/stream")
async def stream_query(req: ChatRequest) -> StreamingResponse:
    """Server-Sent Events streaming endpoint."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="質問が空です。")

    token_gen, sources, sid = _pipeline.stream(
        question=req.question,
        session_id=req.session_id,
        category=req.category,
    )

    def event_stream():
        for token in token_gen:
            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
        # Send sources as final event
        sources_data = [s.model_dump() for s in sources]
        yield f"data: {json.dumps({'sources': sources_data, 'session_id': sid}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/feedback", response_model=FeedbackResponse)
async def feedback(req: FeedbackRequest) -> FeedbackResponse:
    if req.rating not in (1, -1):
        raise HTTPException(status_code=400, detail="rating は 1（役立った）または -1（的外れ）にしてください。")

    record = req.model_dump()
    record["recorded_at"] = datetime.now().isoformat()

    _FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _FEEDBACK_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return FeedbackResponse(message="フィードバックを記録しました。ありがとうございます。")
