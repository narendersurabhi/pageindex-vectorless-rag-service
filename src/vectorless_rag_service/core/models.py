from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class DocumentCreate(BaseModel):
    text: str | None = None


class DocumentRecord(BaseModel):
    document_id: UUID
    filename: str | None
    created_at: datetime


class JobRecord(BaseModel):
    job_id: UUID
    document_id: UUID
    status: JobStatus
    progress: float
    error: str | None = None


class IndexNode(BaseModel):
    node_id: str
    parent_id: str | None
    title: str
    level: int
    page_start: int
    page_end: int
    text_span_ids: list[str]
    children: list[str]


class TextSpan(BaseModel):
    span_id: str
    page: int
    text: str


class IndexArtifact(BaseModel):
    document_id: UUID
    nodes: list[IndexNode]
    spans: list[TextSpan]


class Citation(BaseModel):
    node_id: str
    page: int
    section: str
    title: str
    excerpt: str
    score: float


class QueryTrace(BaseModel):
    visited_nodes: list[str]
    decisions: list[str]


class QueryRequest(BaseModel):
    document_id: UUID
    question: str
    top_k: int = 3
    mode: str = "vectorless"
    include_citations: bool = True


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    trace: QueryTrace


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: dict[str, Any] | None = None


class IdempotencyKey(BaseModel):
    key: str
