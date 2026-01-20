from __future__ import annotations

from fastapi import Header, HTTPException, status

from vectorless_rag_service.config import settings


def api_key_auth(x_api_key: str | None = Header(default=None)) -> None:
    if not settings.auth.enabled:
        return
    if x_api_key != settings.auth.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


__all__ = ["api_key_auth"]
