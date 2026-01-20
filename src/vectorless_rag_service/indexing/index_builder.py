from __future__ import annotations

from uuid import UUID

from vectorless_rag_service.core.interfaces import IndexBuilder
from vectorless_rag_service.core.models import IndexArtifact, IndexNode, TextSpan
from vectorless_rag_service.indexing.parser import iter_sections, parse_text, PageContent


def build_spans(pages: list[PageContent]) -> list[TextSpan]:
    spans: list[TextSpan] = []
    for page in pages:
        for idx, paragraph in enumerate(page.text.split("\n\n"), start=1):
            span_id = f"p{page.page_number}-s{idx}"
            spans.append(TextSpan(span_id=span_id, page=page.page_number, text=paragraph.strip()))
    return spans


class PageIndexBuilder(IndexBuilder):
    def build(self, document_id: UUID, text: str) -> IndexArtifact:
        raise NotImplementedError


class BaselineIndexBuilder(IndexBuilder):
    def __init__(self, max_pages: int = 300) -> None:
        self.max_pages = max_pages

    def build(self, document_id: UUID, text: str) -> IndexArtifact:
        pages = parse_text(text, self.max_pages)
        spans = build_spans(pages)
        nodes: list[IndexNode] = []
        root_id = f"doc-{document_id}"
        nodes.append(
            IndexNode(
                node_id=root_id,
                parent_id=None,
                title="Document",
                level=0,
                page_start=1,
                page_end=len(pages),
                text_span_ids=[span.span_id for span in spans],
                children=[],
            )
        )

        for page in pages:
            page_node_id = f"page-{page.page_number}"
            page_span_ids = [span.span_id for span in spans if span.page == page.page_number]
            nodes.append(
                IndexNode(
                    node_id=page_node_id,
                    parent_id=root_id,
                    title=f"Page {page.page_number}",
                    level=1,
                    page_start=page.page_number,
                    page_end=page.page_number,
                    text_span_ids=page_span_ids,
                    children=[],
                )
            )
            nodes[0].children.append(page_node_id)

            section_idx = 1
            for title, section_text in iter_sections(page.text):
                section_span_ids = [
                    span.span_id
                    for span in spans
                    if span.page == page.page_number and span.text in section_text
                ]
                section_node_id = f"page-{page.page_number}-sec-{section_idx}"
                nodes.append(
                    IndexNode(
                        node_id=section_node_id,
                        parent_id=page_node_id,
                        title=title,
                        level=2,
                        page_start=page.page_number,
                        page_end=page.page_number,
                        text_span_ids=section_span_ids or page_span_ids,
                        children=[],
                    )
                )
                nodes[-2].children.append(section_node_id)
                section_idx += 1

        return IndexArtifact(document_id=document_id, nodes=nodes, spans=spans)
