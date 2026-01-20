from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from uuid import UUID

from vectorless_rag_service.core.models import IndexArtifact, JobRecord, QueryRequest, QueryResponse


class VectorlessRetriever(ABC):
    @abstractmethod
    def retrieve(self, artifact: IndexArtifact, request: QueryRequest) -> QueryResponse:
        raise NotImplementedError


class IndexBuilder(ABC):
    @abstractmethod
    def build(self, document_id: UUID, text: str) -> IndexArtifact:
        raise NotImplementedError


class ArtifactStore(ABC):
    @abstractmethod
    def put(self, document_id: UUID, artifact: IndexArtifact) -> str:
        raise NotImplementedError

    @abstractmethod
    def get(self, document_id: UUID) -> IndexArtifact:
        raise NotImplementedError

    @abstractmethod
    def exists(self, document_id: UUID) -> bool:
        raise NotImplementedError


class LLMClient(ABC):
    @abstractmethod
    def complete_json(self, prompt: str) -> dict[str, object]:
        raise NotImplementedError


class DocumentSource(ABC):
    @abstractmethod
    def load_text(self) -> str:
        raise NotImplementedError


class MetadataStore(ABC):
    @abstractmethod
    def create_document(self, filename: str | None) -> UUID:
        raise NotImplementedError

    @abstractmethod
    def get_document_text(self, document_id: UUID) -> str:
        raise NotImplementedError

    @abstractmethod
    def save_document_text(self, document_id: UUID, text: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_job(self, document_id: UUID) -> UUID:
        raise NotImplementedError

    @abstractmethod
    def update_job(self, job_id: UUID, status: str, progress: float, error: str | None) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_job(self, job_id: UUID) -> JobRecord:
        raise NotImplementedError

    @abstractmethod
    def list_jobs(self) -> Iterable[JobRecord]:
        raise NotImplementedError
