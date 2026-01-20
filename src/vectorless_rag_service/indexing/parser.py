from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from PyPDF2 import PdfReader


@dataclass
class PageContent:
    page_number: int
    text: str


def parse_pdf(path: str, max_pages: int) -> list[PageContent]:
    reader = PdfReader(path)
    pages: list[PageContent] = []
    for idx, page in enumerate(reader.pages[:max_pages], start=1):
        text = page.extract_text() or ""
        pages.append(PageContent(page_number=idx, text=text))
    return pages


def parse_text(text: str, max_pages: int) -> list[PageContent]:
    paragraphs = text.split("\n\n")
    pages: list[PageContent] = []
    current: list[str] = []
    page_number = 1
    for para in paragraphs:
        current.append(para)
        if len("\n\n".join(current)) > 2000:
            pages.append(PageContent(page_number=page_number, text="\n\n".join(current)))
            current = []
            page_number += 1
            if page_number > max_pages:
                break
    if current and page_number <= max_pages:
        pages.append(PageContent(page_number=page_number, text="\n\n".join(current)))
    return pages


HEADING_PATTERN = re.compile(r"^(\d+(?:\.\d+)*)\s+(.+)$")


def iter_sections(text: str) -> Iterable[tuple[str, str]]:
    current_title = "Introduction"
    buffer: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = HEADING_PATTERN.match(stripped)
        if match:
            if buffer:
                yield current_title, "\n".join(buffer)
                buffer = []
            current_title = match.group(2)
        else:
            buffer.append(stripped)
    if buffer:
        yield current_title, "\n".join(buffer)
