from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # LLM
    llm_provider: str = "anthropic"  # "anthropic" or "openai"
    llm_model: str = "claude-haiku-4-5-20251001"

    # Embedding (always OpenAI text-embedding-3-small)
    embedding_model: str = "text-embedding-3-small"

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 100

    # Retrieval
    top_k: int = 5

    # Paths
    upload_dir: Path = Path("data/uploads")
    chroma_dir: Path = Path("chroma_db")

    # Limits
    max_file_size_mb: int = 50

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
