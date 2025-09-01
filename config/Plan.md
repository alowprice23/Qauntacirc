# Plan for the `config` Directory (v4 - Exhaustive & Comprehensive)

## 1. Guiding Philosophy & Core Principles

The `config` directory provides the adaptable "DNA" of the QuantaCirc system. It allows for the declarative configuration of every aspect of the system, from agent behavior to deployment environments. This is a critical component for ensuring that the system is both powerful and manageable.

1.  **Schema-Driven & Validated**: Every configuration file will be validated against a strict, versioned JSON Schema. This is a cornerstone of the system's "irrefutability" claim: the system will refuse to start with an invalid configuration, preventing a wide class of errors.
2.  **Hierarchical & Composable**: A base set of defaults will be provided, which can be overridden by environment-specific configurations. This allows for a clean separation of concerns and makes it easy to manage configurations for different deployment targets (local, dev, staging, prod). The composition of these layers will be deterministic.
3.  **Separation of Code and Configuration**: The behavior of the system should be configurable without changing the code. This makes the system more flexible and easier to manage.
4.  **Secrets Management**: Sensitive data (API keys, credentials) will never be stored in version-controlled configuration files. The configuration system will integrate with a secure secrets management system (like HashiCorp Vault or cloud-specific secret stores).
5.  **Auditability**: All changes to configuration schemas and default values are tracked in Git, providing a clear audit trail.

---

## 2. File-by-File Implementation Plan

This plan details every file within the `config` directory.

### **File: `config/manager.py`**
*   **Purpose**: The central nervous system of the configuration system. The `ConfigManager` class will be responsible for loading, merging, validating, and providing access to the entire system configuration.
*   **Est. LOC**: 350
*   **Dependencies**: `pydantic`, `pyyaml`, `jsonschema`.
*   **Implementation Details**:
    1.  The `ConfigManager` will be initialized with the path to the root configuration file (`quantacirc.yml`).
    2.  It will first load the default configurations from `config/defaults/`.
    3.  Then, it will load the user-provided `quantacirc.yml` and merge it over the defaults.
    4.  Next, it will load the appropriate environment-specific configuration from `config/environments/` and merge it.
    5.  Finally, it will validate the merged configuration against the master JSON Schema.
    6.  The validated configuration will be exposed as a frozen Pydantic model to the rest of the application.
*   **Potential Issues**: Complex merge logic. The merge strategy must be carefully designed to be predictable and deterministic.

### **Sub-directory: `config/schemas/`**
*   **Purpose**: Contains the JSON Schemas that define the "shape" of the configuration data.
*   **Key Files**:
    *   **`project_schema.yaml`**: The master schema that includes all other schemas.
    *   **`agent_schema.yaml`**: A detailed schema for configuring the 10 agents, including their weights in the energy function, their rigor level, and any agent-specific parameters.
    *   **`llm_schema.yaml`**: Schema for configuring LLM providers, including model names, API endpoints, rate limits, and prompt versions.
    *   ... (and so on for `deployment`, `monitoring`, etc.)

### **Sub-directory: `config/defaults/`**
*   **Purpose**: Contains the default, out-of-the-box configuration files.
*   **Key Files**: `project_defaults.yaml`, `agent_defaults.yaml`, etc., corresponding to the schemas.

### **Sub-directory: `config/environments/`**
*   **Purpose**: Environment-specific overrides.
*   **Key Files**: `development.yaml`, `staging.yaml`, `production.yaml`. A `local.yaml` will be in `.gitignore` for developer-specific overrides.

### **Sub-directory: `config/validators/`**
*   **Purpose**: Custom validation logic that cannot be expressed in JSON Schema.
*   **Key Files**:
    *   **`config_validator.py`**: The main Pydantic-based validator.
    *   **`schema_validator.py`**: A utility to validate a YAML file against a schema.
    *   **`api_key_validator.py`**: Checks for the presence (not value) of API keys.
    *   **`environment_validator.py`**: Ensures the environment is consistently configured.
