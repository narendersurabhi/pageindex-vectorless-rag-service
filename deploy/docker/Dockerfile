FROM python:3.11-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv==0.4.20
COPY pyproject.toml README.md ./
RUN uv pip install --system --no-cache -e ".[dev]"

FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd -m appuser
COPY --from=builder /usr/local /usr/local
COPY src ./src
COPY pyproject.toml README.md ./
RUN mkdir -p /app/data && chown -R appuser:appuser /app
USER appuser
CMD ["uvicorn", "vectorless_rag_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
