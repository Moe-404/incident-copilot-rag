from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from runbook_rag.config import get_settings


class Base(DeclarativeBase):
    pass


class QueryEvent(Base):
    __tablename__ = "query_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    question: Mapped[str] = mapped_column(Text)
    service: Mapped[str | None] = mapped_column(String(64), nullable=True)
    generator: Mapped[str] = mapped_column(String(32))
    latency_ms: Mapped[float] = mapped_column(Float)
    citations: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class FeedbackEvent(Base):
    __tablename__ = "feedback_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[str] = mapped_column(String(36), index=True)
    relevant: Mapped[bool]
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


def create_db_engine():
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def initialize_database() -> None:
    Base.metadata.create_all(create_db_engine())


def record_query(**values) -> None:
    with Session(create_db_engine()) as session:
        session.add(QueryEvent(**values))
        session.commit()


def record_feedback(request_id: str, relevant: bool, comment: str | None) -> None:
    with Session(create_db_engine()) as session:
        session.add(FeedbackEvent(request_id=request_id, relevant=relevant, comment=comment))
        session.commit()
