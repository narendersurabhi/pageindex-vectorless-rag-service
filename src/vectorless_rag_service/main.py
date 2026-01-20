from __future__ import annotations

from fastapi import FastAPI

from vectorless_rag_service.api.routes import router
from vectorless_rag_service.config import settings
from vectorless_rag_service.observability.logging import setup_logging
from vectorless_rag_service.observability.middleware import CorrelationIdMiddleware
from vectorless_rag_service.observability.tracing import setup_tracing
from vectorless_rag_service.storage.database import init_db


def create_app() -> FastAPI:
    setup_logging()
    init_db()
    app = FastAPI(title="Vectorless RAG Service", version="0.1.0")
    app.add_middleware(CorrelationIdMiddleware)
    app.include_router(router)
    setup_tracing(app)
    return app


app = create_app()

if settings.env == "dev":
    # enable reload via uvicorn --reload
    pass
