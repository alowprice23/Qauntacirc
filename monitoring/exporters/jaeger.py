# monitoring/exporters/jaeger.py

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, SpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter as JaegerThriftExporter
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased, Sampler
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import Span
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class QuantumAwareSampler(Sampler):
    """
    A custom sampler that makes sampling decisions based on quantum attributes
    in a span. For example, it could always sample traces that contain an
    anomaly or a critical quantum event.
    """
    def should_sample(self, parent_context, trace_id, name, kind, attributes, links):
        # Always sample if a quantum anomaly is detected
        if attributes.get("quantum.anomaly_detected"):
            return trace.SamplingResult.RECORD_AND_SAMPLE
        # Fallback to a default sampler
        return TraceIdRatioBased(0.1).should_sample(parent_context, trace_id, name, kind, attributes, links)

class QuantumSpanProcessor(SpanProcessor):
    """
    A custom span processor to enrich spans with quantum context or perform
    special processing on quantum-related spans.
    """
    def on_start(self, span: Span, parent_context: Optional[trace.Context] = None):
        # Example: Add a new attribute to all quantum-related spans
        if span.name.startswith("quantum_"):
            span.set_attribute("quantum.processed", "true")
        logger.debug(f"Span started: {span.name}")

    def on_end(self, span: Span):
        logger.debug(f"Span ended: {span.name}")

class JaegerExporter:
    """
    Configures and manages the export of OpenTelemetry traces to Jaeger.
    """

    def __init__(self, service_name: str, host: str = "localhost", port: int = 6831, sample_rate: float = 0.1):
        """
        Initializes the Jaeger exporter.
        Args:
            service_name (str): The name of the service that will appear in Jaeger.
            host (str): The hostname of the Jaeger agent.
            port (int): The port of the Jaeger agent.
            sample_rate (float): The base sampling rate for traces (0.0 to 1.0).
        """
        self.service_name = service_name
        self.host = host
        self.port = port
        self.sample_rate = sample_rate

    def setup(self):
        """
        Sets up the OpenTelemetry TracerProvider with the Jaeger exporter,
        including custom samplers and span processors.
        """
        resource = Resource(attributes={"service.name": self.service_name})

        # Using a custom sampler for intelligent, quantum-aware sampling
        sampler = QuantumAwareSampler()

        provider = TracerProvider(sampler=sampler, resource=resource)

        jaeger_exporter = JaegerThriftExporter(
            agent_host_name=self.host,
            agent_port=self.port,
        )

        # Standard batch processor for sending spans to Jaeger
        batch_processor = BatchSpanProcessor(jaeger_exporter)

        # Custom processor for quantum-specific logic
        quantum_processor = QuantumSpanProcessor()

        provider.add_span_processor(batch_processor)
        provider.add_span_processor(quantum_processor)

        # Set the global tracer provider
        trace.set_tracer_provider(provider)

        logger.info(f"Jaeger exporter configured for service '{self.service_name}' at {self.host}:{self.port}")

    def get_tracer(self, name: str) -> trace.Tracer:
        """
        Returns a tracer instance for use in application code.
        """
        return trace.get_tracer(name)
