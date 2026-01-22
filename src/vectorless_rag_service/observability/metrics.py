from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

REQUEST_COUNT = Counter("vrs_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("vrs_request_latency_seconds", "Request latency", ["method", "path"])
ERROR_COUNT = Counter("vrs_errors_total", "Total errors", ["type"])
INDEX_DURATION = Histogram("vrs_index_duration_seconds", "Indexing duration")
JOB_QUEUE_DEPTH = Gauge("vrs_job_queue_depth", "Job queue depth")
