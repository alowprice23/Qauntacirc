from monitoring.metrics import QuantumMetrics, MetricsCollector
from prometheus_client import CollectorRegistry
from typing import Optional

class SystemMetrics:
    """
    Singleton class to manage system-wide metrics.
    """
    _instance: Optional['SystemMetrics'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemMetrics, cls).__new__(cls)
            cls._instance.registry = CollectorRegistry()
            cls._instance.quantum_metrics = QuantumMetrics(registry=cls._instance.registry)
            cls._instance.collector = MetricsCollector(cls._instance.quantum_metrics)
        return cls._instance

    def get_metrics(self) -> QuantumMetrics:
        return self.quantum_metrics

    def get_collector(self) -> MetricsCollector:
        return self.collector

    def get_registry(self) -> CollectorRegistry:
        return self.registry

# Global instance
system_metrics = SystemMetrics()

def get_system_metrics() -> QuantumMetrics:
    """Returns the global QuantumMetrics instance."""
    return system_metrics.get_metrics()

def get_metrics_collector() -> MetricsCollector:
    """Returns the global MetricsCollector instance."""
    return system_metrics.get_collector()

def get_prometheus_registry() -> CollectorRegistry:
    """Returns the global Prometheus CollectorRegistry."""
    return system_metrics.get_registry()

def collect_all_metrics(force: bool = False):
    """Collects all system metrics."""
    get_metrics_collector().collect_if_due(force=force)