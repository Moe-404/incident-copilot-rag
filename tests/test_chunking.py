from runbook_rag.chunking import chunk_markdown, load_corpus


def test_chunking_preserves_sections_and_metadata(knowledge_dir):
    chunks = chunk_markdown(knowledge_dir / "api.md")
    assert [chunk.section for chunk in chunks] == ["Latency", "Verify"]
    assert chunks[0].service == "api"
    assert chunks[0].severity == "high"
    assert chunks[0].source == "knowledge_base/api.md"


def test_chunk_ids_are_deterministic(knowledge_dir):
    first = load_corpus(knowledge_dir)
    second = load_corpus(knowledge_dir)
    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]
