from __future__ import annotations

from vectorless_rag_service.core.interfaces import VectorlessRetriever
from vectorless_rag_service.core.models import IndexArtifact, QueryRequest, QueryResponse
from vectorless_rag_service.retrieval.baseline_retriever import BaselineTreeRetriever


class PageIndexRetriever(VectorlessRetriever):
    def __init__(self) -> None:
        self.fallback = BaselineTreeRetriever()

    def retrieve(self, artifact: IndexArtifact, request: QueryRequest) -> QueryResponse:
        # Placeholder for integration with an official PageIndex library.
        return self.fallback.retrieve(artifact, request)
