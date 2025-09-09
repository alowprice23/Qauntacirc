"""
Performance Benchmark Script

This script runs performance benchmarks for the project.
It uses the timeit module to measure the execution time of critical functions.

Usage:
    python scripts/perf/benchmark.py
"""

import timeit

# --- Configuration ---
NUMBER_OF_RUNS = 10000


def fibonacci(n):
    """A sample function to benchmark (recursive Fibonacci)."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def run_benchmark(name, setup_code, test_code):
    """
    Runs a single benchmark and prints the result.

    Args:
        name (str): The name of the benchmark.
        setup_code (str): The setup code for the benchmark.
        test_code (str): The code to be benchmarked.
    """
    print(f"Running benchmark: {name}...")
    t = timeit.Timer(stmt=test_code, setup=setup_code)
    result = t.timeit(number=NUMBER_OF_RUNS)
    print(f"  - Execution time: {result:.6f} seconds for {NUMBER_OF_RUNS} runs.")


def main():
    """Main function to run all performance benchmarks."""
    print("--- Starting Performance Benchmarks ---")

    # Benchmark 1: Fibonacci function
    setup_fib = "from __main__ import fibonacci"
    test_fib = "fibonacci(10)"
    run_benchmark("Fibonacci(10)", setup_fib, test_fib)

    # Benchmark 2: String concatenation
    setup_str = ""
    test_str = "''.join(str(i) for i in range(100))"
    run_benchmark("String Concatenation", setup_str, test_str)

    print("--- Performance Benchmarks Complete ---")


if __name__ == "__main__":
    main()
