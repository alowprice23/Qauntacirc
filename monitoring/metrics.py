from prometheus_client import Counter, Histogram

generation_counter = Counter("generation_counter", "Counts the number of generation requests")
generation_duration = Histogram("generation_duration_seconds", "Histogram of generation durations")

class QuantumMetrics:
    def register_counter(self, a, b): pass
    def register_histogram(self, a, b): pass
    def log_duration(self, a): return self
    def __enter__(self): pass
    def __exit__(self, a, b, c): pass
    def increment_counter(self, a): pass

def initialize_metrics(config):
    # This function is not needed for now, as the metrics are global.
    pass
