"""
Vercel serverless function entry point for FastAPI.
This is the ASGI handler that Vercel invokes.
"""

from app.main import app


# Vercel expects a WSGI or ASGI app
# For ASGI (FastAPI), we export as 'app'
__all__ = ["app"]
