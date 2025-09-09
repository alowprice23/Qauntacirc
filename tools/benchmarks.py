# tools/benchmarks.py
"""
Benchmarking suite for QuantaCirc.

This module provides tools to run performance benchmarks, track results over
time, and perform comparative analysis between different implementations or
versions of the code.

Key Features:
- A simple benchmarking framework.
- Timing and execution measurement for functions.
- Comparison of different approaches to the same problem.
"""

import time
from typing import Callable, List, Dict, Any

class Benchmark:
    """
    Represents a single benchmark test case.
    """
    def __init__(self, name: str, func: Callable, setup: Callable = lambda: None, iterations: int = 10):
        self.name = name
        self.func = func
        self.setup = setup
        self.iterations = iterations

    def run(self) -> Dict[str, Any]:
        """
        Runs the benchmark and returns performance metrics.
        """
        print(f"Running benchmark: {self.name}...")
        total_time = 0

        for i in range(self.iterations):
            self.setup()
            start_time = time.perf_counter()
            self.func()
            end_time = time.perf_counter()
            total_time += (end_time - start_time)

        avg_time = total_time / self.iterations
        return {
            "name": self.name,
            "iterations": self.iterations,
            "total_time": total_time,
            "avg_time_per_iteration": avg_time,
        }

class BenchmarkSuite:
    """
    Manages and runs a collection of benchmarks.
    """
    def __init__(self):
        self.benchmarks: List[Benchmark] = []

    def add(self, name: str, func: Callable, setup: Callable = lambda: None, iterations: int = 10):
        """Adds a new benchmark to the suite."""
        benchmark = Benchmark(name, func, setup, iterations)
        self.benchmarks.append(benchmark)

    def run_all(self):
        """Runs all benchmarks in the suite and prints a summary."""
        print("--- Starting Benchmark Suite ---")
        results = [b.run() for b in self.benchmarks]
        print("\n--- Benchmark Summary ---")
        for res in results:
            print(
                f"  - {res['name']}:\n"
                f"    Avg Time: {res['avg_time_per_iteration']:.6f}s "
                f"({res['iterations']} iterations)"
            )
        print("-------------------------\n")


if __name__ == '__main__':
    # Example Usage
    suite = BenchmarkSuite()

    # Define some functions to benchmark
    def list_comprehension_task():
        return [i*i for i in range(10000)]

    def map_task():
        return list(map(lambda i: i*i, range(10000)))

    # Add benchmarks to the suite
    suite.add("List Comprehension", list_comprehension_task, iterations=100)
    suite.add("Map Function", map_task, iterations=100)

    # Run the benchmarks
    suite.run_all()
