# config/schemas.py
"""
Configuration Schemas for QuantaCirc.

This module provides JSON schemas for validating the structure and types
of configuration files. These schemas are used by the ConfigValidator
to ensure that any loaded configuration is well-formed before being
used by the application.

The schemas are designed to be extensible, allowing for future additions
to the configuration without breaking validation for existing fields.
"""

from typing import Dict, Final

# A base schema for configuration sections that are currently simple objects
# but are expected to be extended in the future.
BASE_CONFIG_SCHEMA: Final[Dict] = {
    "type": "object",
    "additionalProperties": True,
}

# Schema for the 'project' section of the configuration.
PROJECT_SCHEMA: Final[Dict] = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Name of the project."},
        "version": {"type": "string", "description": "Version of the project."},
    },
    "required": ["name", "version"],
    "additionalProperties": True,
}

# Schema for the 'agents' section of the configuration.
# This could be extended to validate individual agent configurations.
AGENTS_SCHEMA: Final[Dict] = BASE_CONFIG_SCHEMA

# Schema for the 'execution' section of the configuration.
EXECUTION_SCHEMA: Final[Dict] = {
    "type": "object",
    "properties": {
        "default_mode": {"type": "string", "enum": ["simulation", "hardware"]},
    },
    "additionalProperties": True,
}

# Schema for the 'memory' section of the configuration.
MEMORY_SCHEMA: Final[Dict] = BASE_CONFIG_SCHEMA

# Schema for the 'security' section of the configuration.
SECURITY_SCHEMA: Final[Dict] = {
    "type": "object",
    "properties": {
        "api_key_path": {"type": "string"},
    },
    "additionalProperties": True,
}


# The main schema for the entire QuantaCirc configuration file.
# It references the schemas for each top-level section.
QUANTA_CIRC_CONFIG_SCHEMA: Final[Dict] = {
    "type": "object",
    "properties": {
        "project": PROJECT_SCHEMA,
        "agents": AGENTS_SCHEMA,
        "execution": EXECUTION_SCHEMA,
        "memory": MEMORY_SCHEMA,
        "security": SECURITY_SCHEMA,
    },
    "required": ["project"],
    "additionalProperties": False,
}
