# Runbook

## Common failures

### Index job failed
- Check `/v1/jobs/{job_id}` for error.
- Inspect logs for `index_failed`.
- Verify file size/page limits.

### Readiness failing
- Ensure database is reachable.
- Confirm artifact storage path exists.

## Observability

- Logs: structured JSON with request_id and trace IDs.
- Metrics: `/metrics` for Prometheus counters/histograms.
- Traces: Jaeger UI at `http://localhost:16686` when enabled.

## Scaling

- Horizontal scale the API layer (stateless).
- Use shared artifact store (S3) and Postgres for metadata.
- Add a worker queue for indexing if indexing load increases.
