from collections import defaultdict
from typing import Dict, Any, List
import time

class MetricsManager:
    def __init__(self):
        self.counters: Dict[str, int] = defaultdict(int)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.gauges: Dict[str, float] = defaultdict(float)

    def increment_counter(self, name: str, value: int = 1):
        self.counters[name] += value

    def observe_histogram(self, name: str, value: float):
        self.histograms[name].append(value)

    def set_gauge(self, name: str, value: float):
        self.gauges[name] = value

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "counters": dict(self.counters),
            "histograms": {k: {"sum": sum(v), "count": len(v)} for k, v in self.histograms.items()},
            "gauges": dict(self.gauges),
        }

    def track_execution_time(self, name: str):
        return self.execution_time_context(name)

    class execution_time_context:
        def __init__(self, manager: 'MetricsManager', name: str):
            self.manager = manager
            self.name = name
            self.start_time = 0

        def __enter__(self):
            self.start_time = time.time()

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            self.manager.observe_histogram(f"{self.name}_duration_seconds", duration)