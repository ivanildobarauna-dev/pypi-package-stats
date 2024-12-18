import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from src.domain.dto.application_attributes import ApplicationAttributes


class TracingService:
    def __init__(self):
        self._app_atrributes = ApplicationAttributes()
        self.tracer_name = "job-pypi-stats"
        self.resource = Resource.create(
            attributes={
                "service.name": self._app_atrributes.application_name,
                "service.version": self._app_atrributes.application_version,
                "deployment.environment": self._app_atrributes.environment,
            }
        )
        self.trace_provider = TracerProvider(
            resource=self.resource, shutdown_on_exit=False
        )
        trace.set_tracer_provider(self.trace_provider)
        self.span_processor = _SpanProcessor()
        self.span_status = trace.StatusCode
        RequestsInstrumentor().instrument()

    def get_tracer(self):
        return trace.get_tracer(self.tracer_name)


class _SpanProcessor:
    def __init__(self):
        self._setup()

    def _setup(self):
        exporter_address = str(os.getenv("EXPORTER_ADDRESS")) + ":4318/v1/traces"
        exporter = OTLPSpanExporter(endpoint=exporter_address)
        processor = SimpleSpanProcessor(exporter)
        trace.get_tracer_provider().add_span_processor(processor)
