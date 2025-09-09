---
generation_method: "This document is intended to be auto-generated from the Python docstrings in the `/cli` directory using a tool like `mkdocstrings`. The content below is a manually-created placeholder."
---

# API Reference: `cli`

This document provides a reference for the QuantaCirc Command-Line Interface (CLI). The CLI is the primary way for users to interact with the system. The main entry point is `qc`.

## `qc init`

**`cli.commands.init`**

Initializes a new QuantaCirc project in the current directory.

### Usage

```bash
qc init --name "MyNewProject" --template "default"
```

### Arguments

- **`--name`** (str, required): The name of the new project.
- **`--template`** (str, optional): The project template to use. Defaults to `"default"`.

This command creates the necessary directory structure and configuration files for a new project.

---

## `qc generate`

**`cli.commands.generate`**

Generates a new component for the project, such as an agent or a test.

### Usage

```bash
qc generate agent --name "MyCustomAgent"
```

### Subcommands

- **`agent`**: Generates a new agent from a template.
- **`test`**: Generates a new test file.

---

## `qc deploy`

**`cli.commands.deploy`**

Deploys the project to a specified environment.

### Usage

```bash
qc deploy --environment "staging" --skip-tests
```

### Arguments

- **`--environment`** (str, required): The target environment (e.g., `dev`, `staging`, `prod`).
- **`--skip-tests`** (bool, optional): If set, skips running the test suite before deployment.

---

## `qc verify`

**`cli.commands.verify`**

Runs the verification suite for the project.

### Usage

```bash
qc verify --suite "full"
```

### Arguments

- **`--suite`** (str, optional): The verification suite to run. Can be `"full"`, `"constraints"`, or `"proofs"`. Defaults to `"full"`.

This command checks the project for correctness, including running unit tests, property tests, and verifying formal proofs.
