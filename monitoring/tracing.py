# monitoring/tracing.py

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.propagators.composite import CompositePropagator
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

# --- Global Tracer Configuration ---
# In a real application, the exporter would be configured to send to a collector
# like Jaeger or Zipkin. For this implementation, we use a ConsoleSpanExporter.
provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

# Set up context propagation for distributed tracing
propagator = CompositePropagator([TraceContextTextMapPropagator(), B3MultiFormat()])

class QuantumTracer:
    """
    A quantum-aware distributed tracer using OpenTelemetry for creating,
    enriching, and propagating traces across the quantum simulation platform.
    """

    def __init__(self, service_name="quantum_service"):
        """
        Initializes the QuantumTracer.
        Args:
            service_name (str): The name of the service, which will be
                                associated with all traces originating from
                                this tracer.
        """
        self.tracer = trace.get_tracer(service_name)

    def start_span(self, name, context=None, kind=trace.SpanKind.INTERNAL):
        """
        Starts a new span, which represents a unit of work.
        Args:
            name (str): The name of the span.
            context (Context, optional): The parent context. If None, a new
                                         trace is created. Defaults to None.
            kind (SpanKind, optional): The kind of span. Defaults to INTERNAL.
        Returns:
            A context manager for the new span.
        """
        return self.tracer.start_as_current_span(name, context=context, kind=kind)

    def add_quantum_attributes(self, span, system_id, energy, lyapunov_exponent, phase):
        """
        Adds quantum-specific attributes to a span for detailed observability.
        Args:
            span (Span): The span to which the attributes will be added.
            system_id (str): The ID of the quantum system.
            energy (float): The energy level of the system.
            lyapunov_exponent (float): The stability of the system.
            phase (float): The phase of the quantum state.
        """
        if not span:
            span = trace.get_current_span()

        span.set_attribute("quantum.system_id", system_id)
        span.set_attribute("quantum.energy", energy)
        span.set_attribute("quantum.lyapunov_exponent", lyapunov_exponent)
        span.set_attribute("quantum.phase", phase)

    def add_agent_attributes(self, span, agent_name, agent_version, input_params):
        """
        Adds agent-specific attributes to a span.
        Args:
            span (Span): The span to which the attributes will be added.
            agent_name (str): The name of the agent.
            agent_version (str): The version of the agent.
            input_params (dict): The input parameters for the agent execution.
        """
        if not span:
            span = trace.get_current_span()

        span.set_attribute("agent.name", agent_name)
        span.set_attribute("agent.version", agent_version)
        for key, value in input_params.items():
            span.set_attribute(f"agent.input.{key}", str(value))

    def inject_context(self, carrier: dict):
        """
        Injects the current trace context into a carrier dictionary for
        propagation to other services.
        Args:
            carrier (dict): A dictionary to hold the context.
        """
        propagator.inject(carrier)

    def extract_context(self, carrier: dict):
        """
        Extracts trace context from a carrier dictionary to continue a trace
        from another service.
        Args:
            carrier (dict): The dictionary containing the trace context.
        Returns:
            A new context object.
        """
        return propagator.extract(carrier)

    @staticmethod
    def get_current_span():
        """
        Returns the current active span from the context.
        """
        return trace.get_current_span()
