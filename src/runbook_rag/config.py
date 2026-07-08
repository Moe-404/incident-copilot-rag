from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_project_root() -> Path:
    cwd = Path.cwd()
    if (cwd / "knowledge_base").exists():
        return cwd
    parent_root = Path(__file__).resolve().parents[2]
    if (parent_root / "knowledge_base").exists():
        return parent_root
    return cwd


PROJECT_ROOT = _resolve_project_root()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_environment: str = "development"
    database_url: str = f"sqlite:///{PROJECT_ROOT / 'audit.db'}"
    index_path: Path = PROJECT_ROOT / "artifacts/rag_index.joblib"
    knowledge_dir: Path = PROJECT_ROOT / "knowledge_base"
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    top_k: int = 4
    retrieval_threshold: float = 0.01


@lru_cache
def get_settings() -> Settings:
    return Settings()
