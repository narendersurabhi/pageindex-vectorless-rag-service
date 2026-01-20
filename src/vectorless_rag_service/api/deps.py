from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status

from vectorless_rag_service.config import settings


def api_key_auth(x_api_key: str | None = Header(default=None)) -> None:
    if not settings.auth.enabled:
        return
    if x_api_key != settings.auth.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def require_api_key(dep=Depends(api_key_auth)) -> None:  # noqa: ANN001
    return dep
