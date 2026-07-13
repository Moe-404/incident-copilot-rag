from runbook_rag.evaluation import evaluate


def test_evaluation_reports_quality_and_statistics(retriever):
    metrics = evaluate(
        retriever,
        [
            {"question": "p95 latency", "service": "api", "relevant_documents": ["api"]},
            {
                "question": "connection pool wait",
                "service": "database",
                "relevant_documents": ["database"],
            },
        ],
        top_k=1,
    )
    assert metrics["recall_at_k"] == 1.0
    assert metrics["mrr"] == 1.0
    assert metrics["ndcg_at_k"] == 1.0
    assert metrics["recall_at_k_ci95_low"] == 1.0
