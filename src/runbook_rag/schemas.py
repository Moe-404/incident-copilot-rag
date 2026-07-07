from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=5, max_length=1_000)
    service: str | None = Field(default=None, min_length=2, max_length=64)


class Citation(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    section: str
    source: str
    score: float
    excerpt: str


class QueryResponse(BaseModel):
    request_id: str
    answer: str
    generator: str
    index_version: str
    latency_ms: float
    citations: list[Citation]


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str = Field(min_length=36, max_length=36)
    relevant: bool
    comment: str | None = Field(default=None, max_length=1_000)
