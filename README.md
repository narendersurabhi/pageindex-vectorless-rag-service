# Vectorless RAG Service

Production-grade FastAPI microservice implementing vector-less RAG using a PageIndex-style hierarchical index.

## Quickstart (docker-compose)

```bash
docker compose -f deploy/compose/docker-compose.yml up --build
```

Service will be available at `http://localhost:8000`.

## Example requests

```bash
curl -X POST http://localhost:8000/v1/documents \
  -H "X-API-Key: dev-key" \
  -F "file=@./sample.pdf"
```

```bash
curl -X POST http://localhost:8000/v1/documents/{document_id}/index \
  -H "X-API-Key: dev-key"
```

```bash
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key" \
  -d '{"document_id":"<uuid>","question":"What is the overview?","top_k":3}'
```

## How indexing works

1. Documents are parsed into pages.
2. Each page is split into sections via heading detection and paragraphs.
3. A hierarchical index is constructed: Document → Page → Section → Paragraph spans.
4. Index artifacts are stored as JSON for retrieval.

## Retriever selection

`PageIndexRetriever` is the default adapter. It currently delegates to `BaselineTreeRetriever` until an official PageIndex library is wired in. To switch behavior, update the retriever wiring in `api/routes.py`.

## Development

```bash
make setup
make lint
make type
make test
```

## Observability

- Logs: JSON via structlog
- Metrics: `/metrics` (Prometheus)
- Traces: OTLP exporter (configure `VRS_OBSERVABILITY__OTLP_ENDPOINT`)
