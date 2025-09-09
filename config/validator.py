# config/validator.py
"""
Configuration Validation Framework for QuantaCirc.

This module provides the `ConfigValidator` class, which is responsible for
validating configuration dictionaries against a predefined JSON schema.
It is designed to provide clear, actionable error messages when validation
fails, helping users to quickly identify and correct issues in their
configuration files.
"""

from typing import Any, Dict, List, Optional

import jsonschema
from jsonschema.exceptions import ValidationError

from .schemas import QUANTA_CIRC_CONFIG_SCHEMA


class ConfigValidator:
    """
    Validates a configuration dictionary against a JSON schema.

    This class uses the `jsonschema` library to perform validation.
    It can be initialized with a specific schema, or it will default
    to the main QuantaCirc configuration schema.
    """

    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        """
        Initializes the validator with a schema.

        Args:
            schema: A JSON schema to validate against. If None, defaults to
                    QUANTA_CIRC_CONFIG_SCHEMA.
        """
        self.schema = schema or QUANTA_CIRC_CONFIG_SCHEMA
        self._errors: List[str] = []

    @property
    def errors(self) -> List[str]:
        """A list of validation errors found during the last validation."""
        return self._errors

    def validate(self, config_data: Dict[str, Any]) -> bool:
        """
        Validates the given configuration data against the schema.

        Args:
            config_data: The configuration dictionary to validate.

        Returns:
            True if the configuration is valid, False otherwise.
            Errors can be retrieved from the `errors` property.
        """
        self._errors.clear()
        try:
            validator = jsonschema.Draft7Validator(self.schema)
            error_list = sorted(validator.iter_errors(config_data), key=str)
            if not error_list:
                return True

            for error in error_list:
                self._errors.append(self._format_error(error))
            return False
        except Exception as e:
            self._errors.append(f"An unexpected error occurred during validation: {e}")
            return False

    def _format_error(self, error: ValidationError) -> str:
        """Formats a ValidationError into a user-friendly string."""
        path = ".".join(map(str, error.path)) or "root"
        return f"Validation error at '{path}': {error.message}"
