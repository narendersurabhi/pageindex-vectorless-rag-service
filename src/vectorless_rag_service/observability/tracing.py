from __future__ import annotations

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from vectorless_rag_service.config import settings


def setup_tracing(app) -> None:
    resource = Resource.create({"service.name": settings.observability.service_name})
    provider = TracerProvider(resource=resource)
    if settings.observability.otlp_endpoint:
        exporter = OTLPSpanExporter(endpoint=settings.observability.otlp_endpoint)
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()
