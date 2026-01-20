from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import select

from vectorless_rag_service.core.interfaces import MetadataStore
from vectorless_rag_service.core.models import JobRecord, JobStatus
from vectorless_rag_service.storage.database import SessionLocal
from vectorless_rag_service.storage.models import Document, IndexArtifactRecord, Job


class SqlMetadataStore(MetadataStore):
    def create_document(self, filename: str | None) -> UUID:
        with SessionLocal() as session:
            record = Document(filename=filename)
            session.add(record)
            session.commit()
            return UUID(record.id)

    def save_document_text(self, document_id: UUID, text: str) -> None:
        with SessionLocal() as session:
            record = session.get(Document, str(document_id))
            if record is None:
                raise ValueError("document not found")
            record.text = text
            session.commit()

    def get_document_text(self, document_id: UUID) -> str:
        with SessionLocal() as session:
            record = session.get(Document, str(document_id))
            if record is None:
                raise ValueError("document not found")
            return record.text

    def create_job(self, document_id: UUID) -> UUID:
        with SessionLocal() as session:
            job = Job(document_id=str(document_id), status=JobStatus.pending.value, progress=0.0)
            session.add(job)
            session.commit()
            return UUID(job.id)

    def update_job(self, job_id: UUID, status: str, progress: float, error: str | None) -> None:
        with SessionLocal() as session:
            job = session.get(Job, str(job_id))
            if job is None:
                raise ValueError("job not found")
            job.status = status
            job.progress = progress
            job.error = error
            session.commit()

    def get_job(self, job_id: UUID) -> JobRecord:
        with SessionLocal() as session:
            job = session.get(Job, str(job_id))
            if job is None:
                raise ValueError("job not found")
            return JobRecord(
                job_id=UUID(job.id),
                document_id=UUID(job.document_id),
                status=JobStatus(job.status),
                progress=job.progress,
                error=job.error,
            )

    def list_jobs(self) -> Iterable[JobRecord]:
        with SessionLocal() as session:
            for job in session.scalars(select(Job)):
                yield JobRecord(
                    job_id=UUID(job.id),
                    document_id=UUID(job.document_id),
                    status=JobStatus(job.status),
                    progress=job.progress,
                    error=job.error,
                )


class IndexArtifactStore:
    def record(self, document_id: UUID, uri: str) -> None:
        with SessionLocal() as session:
            record = IndexArtifactRecord(document_id=str(document_id), uri=uri)
            session.merge(record)
            session.commit()

    def get_uri(self, document_id: UUID) -> str | None:
        with SessionLocal() as session:
            record = session.get(IndexArtifactRecord, str(document_id))
            if record is None:
                return None
            return record.uri
