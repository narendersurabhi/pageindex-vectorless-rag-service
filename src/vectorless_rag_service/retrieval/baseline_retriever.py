from __future__ import annotations

import math
from collections import Counter

from rapidfuzz import fuzz

from vectorless_rag_service.core.interfaces import VectorlessRetriever
from vectorless_rag_service.core.models import Citation, IndexArtifact, QueryRequest, QueryResponse, QueryTrace


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in text.split() if token.isalnum()]


def score_text(query: str, candidate: str) -> float:
    if not candidate:
        return 0.0
    return fuzz.partial_ratio(query.lower(), candidate.lower()) / 100.0


def bm25_like(query: str, candidate: str) -> float:
    query_tokens = tokenize(query)
    candidate_tokens = tokenize(candidate)
    if not query_tokens or not candidate_tokens:
        return 0.0
    query_counts = Counter(query_tokens)
    candidate_counts = Counter(candidate_tokens)
    score = 0.0
    for token in query_counts:
        tf = candidate_counts[token]
        score += (tf / (tf + 1.5)) * (1 + math.log(1 + query_counts[token]))
    return score / len(candidate_tokens)


class BaselineTreeRetriever(VectorlessRetriever):
    def retrieve(self, artifact: IndexArtifact, request: QueryRequest) -> QueryResponse:
        nodes_by_id = {node.node_id: node for node in artifact.nodes}
        spans_by_id = {span.span_id: span for span in artifact.spans}
        trace = QueryTrace(visited_nodes=[], decisions=[])

        def score_node(node_id: str) -> float:
            node = nodes_by_id[node_id]
            return score_text(request.question, node.title) + bm25_like(request.question, node.title)

        current_ids = [artifact.nodes[0].node_id]
        best_nodes: list[tuple[str, float]] = []

        while current_ids:
            scored = [(node_id, score_node(node_id)) for node_id in current_ids]
            scored.sort(key=lambda item: item[1], reverse=True)
            best_id, best_score = scored[0]
            trace.visited_nodes.append(best_id)
            trace.decisions.append(f"selected {best_id} score={best_score:.3f}")
            best_nodes.append((best_id, best_score))
            children = nodes_by_id[best_id].children
            if not children:
                break
            current_ids = children

        best_nodes.sort(key=lambda item: item[1], reverse=True)
        top_nodes = best_nodes[: request.top_k]
        citations: list[Citation] = []
        for node_id, score in top_nodes:
            node = nodes_by_id[node_id]
            span_texts = [spans_by_id[span_id].text for span_id in node.text_span_ids[:2]]
            excerpt = "\n".join(text for text in span_texts if text)
            citations.append(
                Citation(
                    node_id=node_id,
                    page=node.page_start,
                    section=node.title,
                    title=node.title,
                    excerpt=excerpt,
                    score=score,
                )
            )

        answer = "\n".join(citation.excerpt for citation in citations if citation.excerpt)[:2000]
        if not answer:
            answer = "No relevant content found in the document."

        return QueryResponse(answer=answer, citations=citations, trace=trace)
