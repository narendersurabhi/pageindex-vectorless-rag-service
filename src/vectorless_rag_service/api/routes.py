from __future__ import annotations

import tempfile
import time
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Header, UploadFile
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from vectorless_rag_service.api.deps import require_api_key
from vectorless_rag_service.api.errors import error_response
from vectorless_rag_service.config import settings
from vectorless_rag_service.core.models import DocumentCreate, JobStatus, QueryRequest
from vectorless_rag_service.indexing.index_builder import BaselineIndexBuilder
from vectorless_rag_service.indexing.parser import parse_pdf
from vectorless_rag_service.observability.logging import get_logger
from vectorless_rag_service.observability.metrics import ERROR_COUNT, INDEX_DURATION, JOB_QUEUE_DEPTH
from vectorless_rag_service.retrieval.pageindex_retriever import PageIndexRetriever
from vectorless_rag_service.storage.artifacts import build_artifact_store
from vectorless_rag_service.storage.database import init_db
from vectorless_rag_service.storage.metadata_store import IndexArtifactStore, SqlMetadataStore

router = APIRouter(dependencies=[Depends(require_api_key)])
logger = get_logger()
metadata_store = SqlMetadataStore()
artifact_store = build_artifact_store()
index_record_store = IndexArtifactStore()
index_builder = BaselineIndexBuilder(max_pages=settings.limits.max_pages)
retriever = PageIndexRetriever()


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


@router.get("/readyz")
async def readyz():
    try:
        init_db()
        return {"status": "ready"}
    except Exception as exc:
        ERROR_COUNT.labels("readiness").inc()
        return JSONResponse(status_code=503, content={"status": "error", "detail": str(exc)})


@router.post("/v1/documents")
async def create_document(
    background_tasks: BackgroundTasks,
    payload: Annotated[DocumentCreate | None, Body(default=None)] = None,
    file: UploadFile | None = File(default=None),
    idempotency_key: Annotated[str | None, Header(default=None)] = None,
):
    _ = idempotency_key
    if file is None and (payload is None or payload.text is None):
        error_response(400, "invalid_request", "Provide a file or text payload")

    if file is not None:
        if file.content_type not in {"application/pdf", "text/plain"}:
            error_response(400, "invalid_content_type", "Only PDF or text files allowed")
        contents = await file.read()
        if len(contents) > settings.limits.max_upload_bytes:
            error_response(413, "payload_too_large", "File exceeds size limit")
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(contents)
            tmp_path = Path(tmp.name)
        if file.content_type == "application/pdf":
            pages = parse_pdf(str(tmp_path), settings.limits.max_pages)
            text = "\n\n".join(page.text for page in pages)
        else:
            text = contents.decode("utf-8")
        tmp_path.unlink(missing_ok=True)
        filename = file.filename
    else:
        text = payload.text if payload else ""
        filename = None

    if len(text) > settings.limits.max_text_length:
        error_response(413, "payload_too_large", "Text exceeds size limit")

    document_id = metadata_store.create_document(filename)
    metadata_store.save_document_text(document_id, text)
    logger.info("document_created", document_id=str(document_id))
    return {"document_id": document_id}


@router.post("/v1/documents/{document_id}/index")
async def index_document(
    document_id: UUID,
    background_tasks: BackgroundTasks,
    idempotency_key: Annotated[str | None, Header(default=None)] = None,
):
    _ = idempotency_key
    job_id = metadata_store.create_job(document_id)
    JOB_QUEUE_DEPTH.inc()

    def run_index():
        start = time.time()
        try:
            metadata_store.update_job(job_id, JobStatus.running.value, 0.1, None)
            text = metadata_store.get_document_text(document_id)
            artifact = index_builder.build(document_id, text)
            uri = artifact_store.put(document_id, artifact)
            index_record_store.record(document_id, uri)
            metadata_store.update_job(job_id, JobStatus.succeeded.value, 1.0, None)
            INDEX_DURATION.observe(time.time() - start)
            logger.info("index_complete", document_id=str(document_id), job_id=str(job_id))
        except Exception as exc:
            metadata_store.update_job(job_id, JobStatus.failed.value, 1.0, str(exc))
            ERROR_COUNT.labels("indexing").inc()
            logger.exception("index_failed", document_id=str(document_id), job_id=str(job_id))
        finally:
            JOB_QUEUE_DEPTH.dec()

    background_tasks.add_task(run_index)
    return {"job_id": job_id, "status": JobStatus.pending.value}


@router.get("/v1/jobs/{job_id}")
async def get_job(job_id: UUID):
    job = metadata_store.get_job(job_id)
    return job.model_dump()


@router.post("/v1/query")
async def query_document(request: QueryRequest):
    if not artifact_store.exists(request.document_id):
        error_response(404, "index_not_found", "Index not found for document")
    artifact = artifact_store.get(request.document_id)
    response = retriever.retrieve(artifact, request)
    return response.model_dump()


@router.get("/metrics")
async def metrics():
    return JSONResponse(content=generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
