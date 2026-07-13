import pytest
from pydantic import ValidationError

from runbook_rag import api
from runbook_rag.schemas import QueryRequest


@pytest.mark.asyncio
async def test_api_query_health_and_metrics(monkeypatch, retriever):
    monkeypatch.setattr(api, "retriever", retriever)
    monkeypatch.setattr(api, "index_version", "test-index")
    monkeypatch.setattr(api, "record_query", lambda **kwargs: None)
    health = api.health()
    response = await api.query(QueryRequest(question="How do I fix p95 latency?"))
    metrics = api.metrics()
    assert health["status"] == "healthy"
    assert response.citations
    assert response.generator == "extractive"
    assert b"rag_requests_total" in metrics.body


def test_schema_rejects_short_question():
    with pytest.raises(ValidationError):
        QueryRequest(question="why")
