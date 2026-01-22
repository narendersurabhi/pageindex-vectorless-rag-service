from __future__ import annotations

from fastapi import HTTPException

from vectorless_rag_service.core.models import ErrorResponse


def error_response(status_code: int, code: str, message: str, details: dict | None = None):
    raise HTTPException(
        status_code=status_code,
        detail=ErrorResponse(error_code=code, message=message, details=details).model_dump(),
    )
