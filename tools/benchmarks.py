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

import json
import os

class BenchmarkSuite:
    """
    Manages and runs a collection of benchmarks.
    """
    def __init__(self, baseline_file: str = "benchmark_baseline.json"):
        self.benchmarks: List[Benchmark] = []
        self.baseline_file = baseline_file
        self.baseline_results: Dict[str, Dict[str, Any]] = self._load_baseline()

    def _load_baseline(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.baseline_file):
            with open(self.baseline_file, 'r') as f:
                return json.load(f)
        return {}

    def save_baseline(self, results: List[Dict[str, Any]]):
        """Saves a set of results as the new baseline."""
        baseline_data = {res["name"]: res for res in results}
        with open(self.baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        print(f"Baseline saved to {self.baseline_file}")

    def add(self, name: str, func: Callable, setup: Callable = lambda: None, iterations: int = 10):
        """Adds a new benchmark to the suite."""
        benchmark = Benchmark(name, func, setup, iterations)
        self.benchmarks.append(benchmark)

    def run_all(self, compare_to_baseline: bool = True, regression_threshold: float = 1.2):
        """
        Runs all benchmarks, prints a summary, and checks for regressions.
        """
        print("--- Starting Benchmark Suite ---")
        results = [b.run() for b in self.benchmarks]

        print("\n--- Benchmark Summary ---")
        for res in results:
            summary_line = (
                f"  - {res['name']}:\n"
                f"    Avg Time: {res['avg_time_per_iteration']:.6f}s "
                f"({res['iterations']} iterations)"
            )
            if compare_to_baseline and self.baseline_results.get(res['name']):
                baseline_time = self.baseline_results[res['name']]['avg_time_per_iteration']
                ratio = res['avg_time_per_iteration'] / baseline_time if baseline_time > 0 else float('inf')
                summary_line += f" (Baseline: {baseline_time:.6f}s, Ratio: {ratio:.2f}x)"
                if ratio > regression_threshold:
                    summary_line += " [REGRESSION DETECTED]"

            print(summary_line)

        print("-------------------------\n")
        return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="QuantaCirc Benchmark Runner")
    parser.add_argument("--save-baseline", action="store_true", help="Save the results of this run as the new baseline.")
    args = parser.parse_args()

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
    results = suite.run_all()

    if args.save_baseline:
        suite.save_baseline(results)
