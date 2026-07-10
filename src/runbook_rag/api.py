from __future__ import annotations

import json
import time
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from runbook_rag.config import get_settings
from runbook_rag.database import initialize_database, record_feedback, record_query
from runbook_rag.generation import generate_answer
from runbook_rag.retrieval import HybridRetriever
from runbook_rag.schemas import Citation, FeedbackRequest, QueryRequest, QueryResponse

REQUESTS = Counter("rag_requests_total", "RAG requests", ["generator", "status"])
LATENCY = Histogram("rag_request_latency_seconds", "End-to-end RAG request latency")
RETRIEVAL_SCORE = Histogram("rag_retrieval_score", "Retrieved chunk relevance score")

retriever: HybridRetriever | None = None
index_version = "unknown"


def load_index(path: Path | None = None) -> HybridRetriever:
    global retriever, index_version
    if retriever is None:
        index_path = path or get_settings().index_path
        if not index_path.exists():
            raise RuntimeError("RAG index is missing; run `make index` first")
        payload = __import__("joblib").load(index_path)
        retriever = payload["retriever"]
        index_version = payload["manifest"]["corpus_sha256"][:12]
    return retriever


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    try:
        load_index()
    except RuntimeError:
        pass
    yield


app = FastAPI(
    title="Runbook RAG Incident Assistant",
    description="Grounded incident guidance with citations, evaluation, and audit logging.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    try:
        load_index()
        return {"status": "healthy", "index_version": index_version}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    settings = get_settings()
    started = time.perf_counter()
    request_id = str(uuid4())
    try:
        results = load_index().search(
            request.question,
            top_k=settings.top_k,
            min_score=settings.retrieval_threshold,
            service=request.service,
        )
        generated = await generate_answer(request.question, results, settings)
        elapsed_ms = (time.perf_counter() - started) * 1_000
        citations = [
            Citation(
                chunk_id=result.chunk.chunk_id,
                document_id=result.chunk.document_id,
                title=result.chunk.title,
                section=result.chunk.section,
                source=result.chunk.source,
                score=result.score,
                excerpt=result.chunk.text[:300],
            )
            for result in results
        ]
        for result in results:
            RETRIEVAL_SCORE.observe(result.score)
        REQUESTS.labels(generator=generated.generator, status="success").inc()
        LATENCY.observe(elapsed_ms / 1_000)
        try:
            record_query(
                request_id=request_id,
                question=request.question,
                service=request.service,
                generator=generated.generator,
                latency_ms=elapsed_ms,
                citations=[citation.model_dump() for citation in citations],
            )
        except Exception:
            pass
        return QueryResponse(
            request_id=request_id,
            answer=generated.answer,
            generator=generated.generator,
            index_version=index_version,
            latency_ms=elapsed_ms,
            citations=citations,
        )
    except RuntimeError as exc:
        REQUESTS.labels(generator="none", status="unavailable").inc()
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/feedback", status_code=202)
def feedback(request: FeedbackRequest) -> dict[str, str]:
    try:
        record_feedback(request.request_id, request.relevant, request.comment)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="feedback storage is unavailable") from exc
    return {"status": "accepted"}


@app.get("/index-info")
def index_info() -> dict:
    settings = get_settings()
    manifest_path = settings.index_path.with_suffix(".json")
    if not manifest_path.exists():
        raise HTTPException(status_code=503, detail="index manifest is missing")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
