# monitoring/metrics.py

import time
from prometheus_client import Gauge, Counter, Histogram, REGISTRY

# --- Metric Definitions ---

# Quantum State Metrics
QUANTUM_ENERGY_LEVEL = Gauge(
    "quantum_energy_level",
    "Energy level of the quantum system",
    ["system_id", "qubit_id"],
)
QUANTUM_LYAPUNOV_EXPONENT = Gauge(
    "quantum_lyapunov_exponent",
    "Lyapunov exponent for quantum state stability",
    ["system_id"],
)
QUANTUM_PHASE_ANGLE = Gauge(
    "quantum_phase_angle",
    "Phase angle of a qubit",
    ["system_id", "qubit_id"],
)
QUANTUM_COHERENCE_TIME = Gauge(
    "quantum_coherence_time",
    "Coherence time of the quantum system",
    ["system_id"],
)

# Agent Performance Metrics
AGENT_EXECUTION_TIME = Histogram(
    "agent_execution_time_seconds",
    "Execution time of agents",
    ["agent_name", "agent_version"],
)
AGENT_SUCCESS_RATE = Counter(
    "agent_operations_total",
    "Total number of agent operations by status",
    ["agent_name", "status"],  # status: "success", "failure"
)
AGENT_LLM_CALLS = Counter(
    "agent_llm_calls_total",
    "Total number of LLM calls made by agents",
    ["agent_name", "model_name"],
)

# System Resource Metrics
SYSTEM_CPU_USAGE = Gauge(
    "system_cpu_usage_percent",
    "CPU usage of the monitoring system",
    ["instance"],
)
SYSTEM_MEMORY_USAGE = Gauge(
    "system_memory_usage_bytes",
    "Memory usage of the monitoring system",
    ["instance"],
)
SYSTEM_ACTIVE_CONNECTIONS = Gauge(
    "system_active_connections",
    "Number of active connections",
    ["instance", "service"],
)

# Mathematical Convergence Metrics
CONVERGENCE_ERROR = Gauge(
    "mathematical_convergence_error",
    "Error term in a mathematical convergence process",
    ["algorithm", "iteration"],
)
CONVERGENCE_RESIDUAL = Gauge(
    "mathematical_convergence_residual",
    "Residual value in an iterative solver",
    ["algorithm", "iteration"],
)


class QuantumMetrics:
    """
    A centralized class for managing and recording quantum-aware metrics.
    Integrates with Prometheus for metric collection and exposure.
    """

    def __init__(self, instance_name="default_instance"):
        """
        Initializes the QuantumMetrics collector.
        Args:
            instance_name (str): The name of the instance for system metrics.
        """
        self.instance_name = instance_name

    def record_quantum_state(self, system_id, qubit_id, energy, lyapunov, phase, coherence):
        """
        Records the current state of a quantum system.
        """
        QUANTUM_ENERGY_LEVEL.labels(system_id=system_id, qubit_id=qubit_id).set(energy)
        QUANTUM_LYAPUNOV_EXPONENT.labels(system_id=system_id).set(lyapunov)
        QUANTUM_PHASE_ANGLE.labels(system_id=system_id, qubit_id=qubit_id).set(phase)
        QUANTUM_COHERENCE_TIME.labels(system_id=system_id).set(coherence)

    def record_agent_execution(self, agent_name, agent_version, duration, success):
        """
        Records the performance of an agent execution.
        """
        AGENT_EXECUTION_TIME.labels(agent_name=agent_name, agent_version=agent_version).observe(duration)
        status = "success" if success else "failure"
        AGENT_SUCCESS_RATE.labels(agent_name=agent_name, status=status).inc()

    def record_llm_usage(self, agent_name, model_name):
        """
        Records a call to a large language model.
        """
        AGENT_LLM_CALLS.labels(agent_name=agent_name, model_name=model_name).inc()

    def record_system_resources(self, cpu_usage, memory_usage, active_connections, service_name):
        """
        Records system resource utilization.
        """
        SYSTEM_CPU_USAGE.labels(instance=self.instance_name).set(cpu_usage)
        SYSTEM_MEMORY_USAGE.labels(instance=self.instance_name).set(memory_usage)
        SYSTEM_ACTIVE_CONNECTIONS.labels(instance=self.instance_name, service=service_name).set(active_connections)

    def record_convergence_metric(self, algorithm, iteration, error, residual):
        """
        Records a mathematical convergence metric.
        """
        CONVERGENCE_ERROR.labels(algorithm=algorithm, iteration=iteration).set(error)
        CONVERGENCE_RESIDUAL.labels(algorithm=algorithm, iteration=iteration).set(residual)

    @staticmethod
    def get_registry():
        """
        Returns the Prometheus registry for integration with an exporter.
        """
        return REGISTRY
