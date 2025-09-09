"""
Test Automation Script

This script automates the execution of tests for the project.
It handles the following tasks:
- Runs unit tests using pytest.
- Generates a code coverage report.
- Includes a placeholder for performance testing.

Usage:
    python scripts/test.py [--all | --unit | --performance]
"""

import os
import subprocess
import sys

# --- Configuration ---
TEST_DIR = "tests"
COVERAGE_DIR = "htmlcov"
PYTEST_ARGS = ["-v", "--cov=.", f"--cov-report=html:{COVERAGE_DIR}"]


def run_unit_tests():
    """Runs unit tests using pytest and generates a coverage report."""
    print("Running unit tests...")
    if not os.path.exists(TEST_DIR):
        print(f"Creating dummy test directory '{TEST_DIR}'...")
        os.makedirs(TEST_DIR)
        with open(os.path.join(TEST_DIR, "test_dummy.py"), "w") as f:
            f.write("def test_example():\n")
            f.write("    assert True\n")

    try:
        subprocess.check_call(["pytest", *PYTEST_ARGS, TEST_DIR])
        print("Unit tests completed successfully.")
        print(f"Coverage report generated in '{COVERAGE_DIR}'.")
    except subprocess.CalledProcessError as e:
        print(f"Unit tests failed with exit code {e.returncode}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'pytest' not found. Please install it.", file=sys.stderr)
        sys.exit(1)


def run_performance_tests():
    """Runs performance tests (placeholder)."""
    print("Running performance tests...")
    # This is a placeholder for actual performance tests.
    # In a real project, you would use a tool like `pytest-benchmark`.
    print("Performance tests are not implemented yet.")


def main(args):
    """Main function to run the specified tests."""
    print("--- Starting Test Execution ---")
    if not args or "--all" in args:
        run_unit_tests()
        run_performance_tests()
    elif "--unit" in args:
        run_unit_tests()
    elif "--performance" in args:
        run_performance_tests()
    else:
        print(f"Unknown option: {args[0]}", file=sys.stderr)
        print("Usage: python scripts/test.py [--all | --unit | --performance]", file=sys.stderr)
        sys.exit(1)
    print("--- Test Execution Complete ---")


if __name__ == "__main__":
    main(sys.argv[1:])
