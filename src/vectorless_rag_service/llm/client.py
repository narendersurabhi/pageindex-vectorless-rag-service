from __future__ import annotations

from vectorless_rag_service.core.interfaces import LLMClient


class DisabledLLMClient(LLMClient):
    def complete_json(self, prompt: str) -> dict[str, object]:
        raise RuntimeError("LLM navigation is disabled")
