from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ---------- Document ----------

class DocumentMeta(BaseModel):
    doc_id: str
    filename: str
    file_type: str
    size_bytes: int
    page_count: int
    category: str = "general"
    uploaded_at: datetime = datetime.now()


class DocumentListResponse(BaseModel):
    documents: list[DocumentMeta]
    total: int


class DeleteResponse(BaseModel):
    doc_id: str
    message: str


# ---------- Chat ----------

class Source(BaseModel):
    doc_id: str
    filename: str
    page: int
    score: float
    excerpt: str


class ChatRequest(BaseModel):
    question: str
    category: Optional[str] = None  # metadata filter
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    session_id: str


# ---------- Feedback ----------

class FeedbackRequest(BaseModel):
    session_id: str
    question: str
    answer: str
    rating: int  # 1 = helpful, -1 = unhelpful
    comment: str = ""


class FeedbackResponse(BaseModel):
    message: str
