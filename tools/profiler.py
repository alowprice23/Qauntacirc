# tools/profiler.py
"""
Performance profiling tools for QuantaCirc.

This module provides utilities to profile the execution of functions, helping to
identify performance bottlenecks in critical paths like energy calculations and
agent operations.

Key Features:
- Context manager for easy profiling of code blocks.
- Function decorator for profiling entire functions.
- Reporting of profiling results, sorted by time consumption.
"""

import cProfile
import pstats
import io
from functools import wraps
from typing import Callable, Any

class Profiler:
    """
    A context manager and utility for profiling code execution.
    """
    def __init__(self, sort_by='cumulative'):
        self.pr = cProfile.Profile()
        self.sort_by = sort_by
        self.results = None

    def __enter__(self):
        self.pr.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pr.disable()
        self.generate_stats()

    def generate_stats(self):
        """
        Generates and stores a printable version of the profiling statistics.
        """
        s = io.StringIO()
        ps = pstats.Stats(self.pr, stream=s).sort_stats(self.sort_by)
        ps.print_stats()
        self.results = s.getvalue()

    def print_stats(self, line_limit=20):
        """
        Prints the collected profiling statistics to the console.
        """
        if self.results:
            print("\n--- PROFILING RESULTS ---")
            for line in self.results.splitlines()[:line_limit]:
                print(line)
            print("-------------------------\n")
        else:
            print("No profiling data collected.")

def profile_function(func: Callable) -> Callable:
    """
    A decorator that profiles a function's execution.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        with Profiler() as p:
            result = func(*args, **kwargs)
        print(f"Profiling for function '{func.__name__}':")
        p.print_stats()
        return result
    return wrapper

if __name__ == '__main__':
    # Example Usage

    # 1. Using the context manager
    def example_calculation():
        """A dummy function to simulate work."""
        total = 0
        for i in range(10**6):
            total += i
        return total

    print("Profiling with context manager...")
    with Profiler() as p:
        example_calculation()
    p.print_stats(10)

    # 2. Using the decorator
    @profile_function
    def another_example_task():
        """Another dummy function."""
        import time
        time.sleep(0.1)
        [x*x for x in range(1000)]

    print("Profiling with decorator...")
    another_example_task()
