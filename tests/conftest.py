from pathlib import Path

import pytest

from runbook_rag.retrieval import HybridRetriever


@pytest.fixture
def knowledge_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "knowledge"
    directory.mkdir()
    (directory / "api.md").write_text(
        "# API Runbook\n\nservice: api\nseverity: high\n\n"
        "## Latency\n\nCheck p95 latency and roll back a bad deployment.\n\n"
        "## Verify\n\nConfirm latency stays normal for fifteen minutes.",
        encoding="utf-8",
    )
    (directory / "database.md").write_text(
        "# Database Runbook\n\nservice: database\nseverity: critical\n\n"
        "## Connections\n\nInspect pool wait time and long-running sessions.",
        encoding="utf-8",
    )
    return directory


@pytest.fixture
def retriever(knowledge_dir):
    from runbook_rag.chunking import load_corpus

    return HybridRetriever.build(load_corpus(knowledge_dir))
