from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from typing import Optional, Dict, Any

class QuantumTracer:
    """
    OpenTelemetry distributed tracing for QuantaCirc.
    """
    def __init__(self, service_name: str = "QuantaCirc", jaeger_exporter_config: Optional[Dict] = None):
        self.service_name = service_name
        self.provider = TracerProvider(
            resource=Resource.create({"service.name": self.service_name})
        )

        # Use a console exporter for now, will be replaced by Jaeger
        self.processor = BatchSpanProcessor(ConsoleSpanExporter())
        self.provider.add_span_processor(self.processor)

        trace.set_tracer_provider(self.provider)
        self.tracer = trace.get_tracer(__name__)

    def get_tracer(self):
        return self.tracer

    def start_span(self, name: str, context: Optional[Any] = None, attributes: Optional[Dict[str, Any]] = None):
        """Starts a new span."""
        return self.tracer.start_as_current_span(name, context=context, attributes=attributes)

class TraceManager:
    """Manages tracing context and propagation."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TraceManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.tracer = QuantumTracer().get_tracer()
        return cls._instance

    def get_current_span(self):
        return trace.get_current_span()

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        span = self.get_current_span()
        if span.is_recording():
            span.add_event(name, attributes)

    def set_attribute(self, key: str, value: Any):
        span = self.get_current_span()
        if span.is_recording():
            span.set_attribute(key, value)