# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DocuMate** — 社内ナレッジRAG型Q&Aアプリ (MVP)

A RAG (Retrieval-Augmented Generation) application that lets employees query internal documents (PDF/Word/Markdown/TXT) via a chat interface. The system retrieves relevant chunks from a vector DB and uses an LLM to generate grounded, citation-backed answers.

## Planned Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| RAG Framework | LangChain or LlamaIndex |
| LLM | OpenAI GPT-4o-mini / Anthropic Claude Haiku |
| Embedding | OpenAI `text-embedding-3-small` (1,536 dims) |
| Vector DB | Chroma (MVP) → Pinecone/Weaviate (production) |
| Document Parsing | PyPDF, python-docx, unstructured |
| Backend | FastAPI |
| Frontend | Streamlit (MVP) → Next.js (future) |
| Deploy | Render or Railway |
| Tests | pytest |

## Architecture

```
Browser → Streamlit → FastAPI → [Document Loader | Chroma Vector DB | LLM API]
```

The backend is split into independent modules:
- **Document ingestion pipeline**: upload → parse → chunk → embed → store in Chroma
- **Query pipeline**: question → embed → hybrid search (vector + BM25) → inject context → LLM generate → return answer + citations
- **Streamlit UI**: chat screen, document management screen, settings screen

## Chunking Rules

- Chunk size: 500–1,000 tokens with 100-token overlap
- Each chunk carries metadata: filename, page number, created date, category

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in API keys
cp .env.example .env

# Run backend (http://localhost:8000, auto-reload)
uvicorn app.main:app --reload

# Run frontend (http://localhost:8501)
streamlit run frontend/app.py

# Run all tests (no API keys required — all external calls are mocked)
python -m pytest tests/ -v

# Run a single test file
python -m pytest tests/test_loader.py -v
```

> On Windows the `python` alias may point to the Store stub. Use the full path if needed:
> `C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe -m pytest`

## Key Design Principles

- **Loose coupling**: RAG logic, UI, and API are separate modules with dependency injection via interfaces — changes in one module must not cascade
- **Test-first on F-01 through F-07**: write pytest unit tests before implementing each core feature
- **Early integration**: the first milestone (ticket #006) is a full end-to-end loop with a single file and single question — verify this before building out features
- **Hallucination suppression**: every LLM response must include source citations (document name + page number); prompt templates must explicitly instruct the model not to answer beyond the retrieved context

## Ticket Labels (GitHub Issues)

`type:feature`, `type:bug`, `type:refactor`, `priority:high/mid/low`, `area:backend/frontend/infra`

## KPIs to Keep in Mind

- Answer accuracy: ≥80% on 50 test questions
- Average response time: ≤10 seconds
- Source citation accuracy: ≥95%
- Unit test coverage: ≥70% on core modules
