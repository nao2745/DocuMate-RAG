"""FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.chat import router as chat_router
from app.api.documents import router as documents_router

app = FastAPI(
    title="DocuMate API",
    description="社内ドキュメントRAG型Q&Aアプリ",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Streamlit runs on a different port
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router)
app.include_router(chat_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# Serve static files (Vercel-ready)
public_dir = Path(__file__).parent.parent / "public"
if public_dir.exists():
    app.mount("/static", StaticFiles(directory=public_dir), name="static")


# Serve index.html for SPA routing (catch-all)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str) -> FileResponse:
    """Serve SPA index.html for all non-API routes."""
    index_path = public_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return FileResponse(public_dir / "index.html") if (public_dir / "index.html").exists() else {"error": "Not Found"}
