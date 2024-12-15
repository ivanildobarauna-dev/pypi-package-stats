from abc import ABC, abstractmethod
from opentelemetry.sdk.trace.export import SpanExporter

class ITelemetryExpoter(ABC):
    def __init__(self, expoter: SpanExporter):

