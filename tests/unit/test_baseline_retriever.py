from uuid import uuid4

from vectorless_rag_service.core.models import IndexArtifact, IndexNode, QueryRequest, TextSpan
from vectorless_rag_service.retrieval.baseline_retriever import BaselineTreeRetriever


def test_retriever_returns_citation():
    document_id = uuid4()
    spans = [TextSpan(span_id="s1", page=1, text="Introduction to RAG")]
    nodes = [
        IndexNode(
            node_id="root",
            parent_id=None,
            title="Document",
            level=0,
            page_start=1,
            page_end=1,
            text_span_ids=["s1"],
            children=[],
        )
    ]
    artifact = IndexArtifact(document_id=document_id, nodes=nodes, spans=spans)
    request = QueryRequest(document_id=document_id, question="RAG", top_k=1)

    response = BaselineTreeRetriever().retrieve(artifact, request)

    assert response.citations
    assert response.citations[0].page == 1
