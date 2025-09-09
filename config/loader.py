# config/loader.py
"""
Configuration Loader for QuantaCirc.

This module provides the `ConfigLoader` class, which is responsible for
loading, merging, and validating configuration from one or more YAML files.

Features:
- Loads configuration from YAML files.
- Merges multiple configuration files hierarchically.
- Substitutes environment variables in the format ${VAR}.
- Validates the final configuration against a JSON schema.
"""

import os
import re
from typing import Any, Dict, Optional

import yaml

from core.types import QuantaCircConfig
from .validator import ConfigValidator


class ConfigLoader:
    """Loads, merges, and validates configuration from YAML files."""

    def __init__(self, validator: Optional[ConfigValidator] = None):
        """
        Initializes the loader with a validator.

        Args:
            validator: An instance of ConfigValidator. If None, a default
                       one will be created.
        """
        self.validator = validator or ConfigValidator()

    def load_config(self, *config_paths: str) -> QuantaCircConfig:
        """
        Loads and merges configuration from multiple YAML files.

        The files are merged in the order they are provided. Values in later
        files will overwrite values in earlier ones.

        Args:
            *config_paths: A sequence of paths to YAML configuration files.

        Returns:
            A validated QuantaCircConfig object.

        Raises:
            FileNotFoundError: If a config file is not found.
            ValueError: If the configuration is invalid or an env var is not set.
        """
        merged_config: Dict[str, Any] = {}
        for path in config_paths:
            with open(path, 'r') as f:
                raw_content = f.read()

            substituted_content = self._substitute_env_vars(raw_content)
            config_data = self._load_yaml(substituted_content)

            if not isinstance(config_data, dict):
                raise ValueError(f"Configuration file at {path} must be a dictionary.")

            if config_data:
                merged_config = self._deep_merge(merged_config, config_data)

        if not self.validator.validate(merged_config):
            errors = "\n".join(self.validator.errors)
            raise ValueError(f"Configuration validation failed:\n{errors}")

        return QuantaCircConfig(**merged_config)

    def _substitute_env_vars(self, raw_content: str) -> str:
        """Substitutes environment variables in the format ${VAR}."""
        pattern = re.compile(r'\$\{([A-Z0-9_]+)\}')

        def replacer(match):
            var_name = match.group(1)
            value = os.environ.get(var_name)
            if value is None:
                raise ValueError(f"Environment variable '{var_name}' is not set.")
            return value

        return pattern.sub(replacer, raw_content)

    def _deep_merge(self, base: Dict, new: Dict) -> Dict:
        """Recursively merges two dictionaries."""
        for key, value in new.items():
            if isinstance(base.get(key), dict) and isinstance(value, dict):
                base[key] = self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base

    def _load_yaml(self, content: str) -> Dict:
        """Loads YAML content safely."""
        try:
            return yaml.safe_load(content) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML: {e}")
