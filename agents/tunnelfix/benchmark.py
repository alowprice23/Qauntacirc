"""
Mock Benchmarking for TunnelFix Agent
"""
import time
import random

class MockBenchmark:
    """
    A mock benchmarking class that simulates running code and measuring
    its performance.
    """
    def run(self, code: str) -> float:
        """
        "Runs" the code and returns a mock execution time.
        """
        # Simulate work by sleeping for a short time
        # The performance is based on the length of the code, with some randomness
        base_time = 0.01 + len(code) * 1e-6
        noise = random.uniform(-0.005, 0.005)
        exec_time = base_time + noise
        time.sleep(exec_time)
        return exec_time
