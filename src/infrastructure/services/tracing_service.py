from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from src.domain.dto.application_attributes import ApplicationAttributes


class TracingService:
    def __init__(self):
        self._app_atrributes = ApplicationAttributes()
        self.resource = Resource.create(
            attributes={
                "service.name": self._app_atrributes.application_name,
                "service.version": self._app_atrributes.application_version,
                "deployment.environment": self._app_atrributes.environment,
                "container.id": self._app_atrributes.container_id,
                "container.image": self._app_atrributes.container_image,
            }
        )
        self.trace_provider = TracerProvider(resource=self.resource)
        trace.set_tracer_provider(self.trace_provider)
        self.span_processor = _SpanProcessor()

    def new_trace(self):
        return trace.get_tracer(__name__)


class _SpanProcessor:
    def __init__(self):
        self._setup()

    def _setup(self):
        exporter = OTLPSpanExporter(
            endpoint="node-metrics-ba28.ivanildobarauna.dev:4318", insecure=True
        )
        processor = SimpleSpanProcessor(exporter)
        trace.get_tracer_provider().add_span_processor(processor)
