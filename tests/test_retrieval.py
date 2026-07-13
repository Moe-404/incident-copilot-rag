import json

from runbook_rag.retrieval import HybridRetriever, build_index


def test_hybrid_search_returns_relevant_document(retriever):
    results = retriever.search("p95 latency after deployment", top_k=1)
    assert results[0].chunk.document_id == "api"
    assert results[0].score > 0


def test_metadata_filter_limits_service(retriever):
    results = retriever.search("latency connections", service="database")
    assert results
    assert all(result.chunk.service == "database" for result in results)


def test_index_round_trip_has_versioned_manifest(knowledge_dir, tmp_path):
    path = tmp_path / "artifacts" / "rag_index.joblib"
    manifest = build_index(knowledge_dir, path)
    restored = HybridRetriever.load(path)
    saved = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    assert restored.search("database pool")[0].chunk.document_id == "database"
    assert saved["corpus_sha256"] == manifest["corpus_sha256"]
