# Developer Guide

Welcome to the QuantaCirc Developer Guide. This guide is for those who wish to contribute to the development of the QuantaCirc system itself.

## 1. Repository Structure

The QuantaCirc repository is organized into several top-level directories, each with a specific purpose:

- **`/core`**: The core engine and fundamental data structures.
- **`/agents`**: The agent implementations.
- **`/math_utils`**: The library of mathematical functions.
- **`/llm`**: Clients for large language models.
- **`/messaging`**: The asynchronous messaging system.
- **`/cli`**: The command-line interface.
- **`/deployment`**: Deployment scripts and configurations (Docker, k8s, etc.).
- **`/docs`**: The documentation source files.
- **`/proofs`**: Formal proofs of system properties.
- **`/tests`**: The test suite.

A more detailed overview of the system's components can be found in the [Architecture document](../architecture.md).

## 2. Setting Up a Development Environment

To get started with development, you will need Python 3.11+ and `pip`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/QuantaCirc/quantacirc.git
    cd quantacirc
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    The project uses `pyproject.toml` to manage dependencies. Install all the required packages for development, including optional dependencies for formal verification and monitoring, using the following command:
    ```bash
    pip install -e .[dev,formal,monitoring]
    ```
    This command installs the project in "editable" mode (`-e`) and includes the optional dependency groups `dev`, `formal`, and `monitoring`, which are defined in the `pyproject.toml` file.

## 3. Running Tests

QuantaCirc has a comprehensive test suite. To run all tests, use the `scripts/test.py` script:

```bash
python scripts/test.py
```

This will run unit tests, integration tests, and property-based tests.

## 4. Coding Standards

- All code must be formatted with `black`.
- All code must pass the linter (`flake8` or similar). The project includes a `tools/linter.py` script.
- All public functions and classes must have comprehensive docstrings in the Google style, as these are used to generate the API documentation.

## 5. Contribution Process

1.  Create a fork of the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes, including adding or updating tests.
4.  Ensure all tests pass and the code meets the coding standards.
5.  Submit a pull request to the main repository.

Your pull request will be reviewed by the core team. Thank you for contributing to QuantaCirc!
