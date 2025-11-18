# messaging/middleware/validation.py

"""
Middleware for message validation, including schema, state, and security checks.
"""
from __future__ import annotations

import logging
from typing import Any, Optional, Type

from pydantic import BaseModel, ValidationError

from core.exceptions import QuantumStateError, SchemaValidationError
from core.state_space import StateSpace
from core.types import QCState
from messaging.topic_manager import TopicManager

log = logging.getLogger(__name__)

class ValidationMiddleware:
    """
    Provides a set of methods for validating incoming messages against
    pre-defined schemas, quantum state consistency, and security rules.
    """

    def __init__(self, topic_manager: TopicManager, state_space: Optional[StateSpace] = None):
        """
        Initializes the ValidationMiddleware.

        Args:
            topic_manager: An instance of TopicManager to resolve topic schemas.
            state_space: An instance of StateSpace to validate quantum states.
        """
        if not isinstance(topic_manager, TopicManager):
            raise TypeError("topic_manager must be an instance of TopicManager.")
        self.topic_manager = topic_manager

        if state_space and not isinstance(state_space, StateSpace):
            raise TypeError("state_space must be an instance of StateSpace.")
        self.state_space = state_space

    def validate_payload_schema(self, subject: str, payload_data: Any) -> None:
        """
        Validates the message payload against the registered schema for the topic.

        Args:
            subject: The subject of the message.
            payload_data: The deserialized message payload object.

        Raises:
            SchemaValidationError: If the payload does not match the schema or
                                   if no schema is registered for the topic.
        """
        expected_schema: Type[BaseModel] = self.topic_manager.get_schema_for_topic(subject)

        if not expected_schema:
            # Depending on system policy, this could be a warning or an error.
            # For strict systems, we'll treat it as an error.
            raise SchemaValidationError(f"No schema registered for subject '{subject}'. Cannot validate.")

        if not isinstance(payload_data, expected_schema):
            raise SchemaValidationError(
                f"Payload for subject '{subject}' has type {type(payload_data).__name__}, "
                f"but expected schema {expected_schema.__name__}."
            )

        # The payload is already a Pydantic model, so its structure is valid.
        # We could re-validate it here for extra safety, but it's often redundant.
        try:
            expected_schema.model_validate(payload_data.model_dump())
        except ValidationError as e:
            raise SchemaValidationError(f"Payload for '{subject}' failed re-validation.") from e

        log.debug(f"Payload for '{subject}' successfully validated against schema '{expected_schema.__name__}'.")

    def validate_quantum_state_consistency(self, context: QCState) -> None:
        """
        Validates the consistency and validity of the quantum state context.

        Args:
            context: The QCState object from the message.

        Raises:
            QuantumStateError: If the state is invalid or inconsistent.
        """
        if not self.state_space:
            log.warning("No state_space configured in ValidationMiddleware; skipping quantum state validation.")
            return

        if not self.state_space.is_valid_state(context):
            raise QuantumStateError(f"Received quantum state {context.id} is not valid in the current state space.")

        # Additional consistency checks from the model itself can be re-run here.
        try:
            context.model_validate(context.model_dump())
        except ValueError as e:
            raise QuantumStateError(f"QCState internal validation failed: {e}") from e

        log.debug(f"Quantum state {context.id} passed consistency validation.")

    def sanitize_payload(self, payload_data: Any) -> Any:
        """
        Placeholder for payload sanitization logic.

        This method should be implemented to remove or neutralize any potentially
        malicious or malformed content from the payload before it is processed
        by business logic.

        Args:
            payload_data: The deserialized payload data.

        Returns:
            The sanitized payload data.
        """
        # TODO: Implement actual sanitization logic based on security requirements.
        # Examples:
        # - Stripping unknown fields from dictionaries.
        # - Limiting string lengths.
        # - Checking for suspicious patterns (e.g., SQL injection attempts).
        log.warning(f"Payload sanitization is a placeholder and not yet implemented.")
        return payload_data

    def run_all_validations(self, subject: str, payload_data: Any, quantum_context: Optional[QCState]) -> Any:
        """
        Runs all configured validation and sanitization checks on a message.

        Args:
            subject: The message subject.
            payload_data: The deserialized message payload.
            quantum_context: The optional quantum context from the message.

        Returns:
            The sanitized payload data.

        Raises:
            SchemaValidationError: If payload schema validation fails.
            QuantumStateError: If quantum state validation fails.
        """
        log.debug(f"Running all validations for message on subject '{subject}'.")

        # 1. Schema Validation
        self.validate_payload_schema(subject, payload_data)

        # 2. Quantum State Validation
        if quantum_context:
            self.validate_quantum_state_consistency(quantum_context)

        # 3. Sanitization
        sanitized_payload = self.sanitize_payload(payload_data)

        return sanitized_payload
