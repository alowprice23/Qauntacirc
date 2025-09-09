# config/__init__.py
"""
Configuration Management System for QuantaCirc.

This package provides a hierarchical configuration system with support for
YAML files, environment variable substitution, and schema validation.

The main components are:
- `ConfigLoader`: Loads, merges, and validates configuration files.
- `ConfigValidator`: Validates configuration data against a JSON schema.
"""

from .loader import ConfigLoader
from .validator import ConfigValidator

__all__ = ["ConfigLoader", "ConfigValidator"]
