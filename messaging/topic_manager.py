# messaging/topic_manager.py

"""
Manages application-level topic schemas, routing, and lifecycle.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

log = logging.getLogger(__name__)

class TopicManager:
    """
    Provides an application-level registry for managing topic schemas and
    other metadata, separate from the NATS server's view of subjects.
    """

    def __init__(self, schema_registry_client: Optional[Any] = None):
        """
        Initializes the TopicManager.

        Args:
            schema_registry_client: A client for an external schema registry
                                    (e.g., Confluent Schema Registry).
                                    This is a placeholder for future integration.
        """
        # Simple in-memory storage for topic schemas.
        self._topic_schemas: Dict[str, Type[BaseModel]] = {}
        self._access_control_rules: Dict = {} # Placeholder for ACLs

        if schema_registry_client:
            log.warning("External schema registry client provided but not yet implemented.")
        self.schema_registry_client = schema_registry_client

    def register_topic(
        self,
        topic_subject: str,
        schema: Type[BaseModel],
        overwrite: bool = False
    ) -> None:
        """
        Registers a topic subject with its corresponding Pydantic schema.

        Args:
            topic_subject: The NATS subject string for the topic.
            schema: The Pydantic model class that defines the topic's message structure.
            overwrite: If True, allows overwriting an existing registration.
        """
        if not isinstance(topic_subject, str) or not topic_subject:
            raise ValueError("topic_subject must be a non-empty string.")
        if not isinstance(schema, type) or not issubclass(schema, BaseModel):
            raise TypeError("schema must be a Pydantic BaseModel class.")

        if topic_subject in self._topic_schemas and not overwrite:
            raise ValueError(f"Topic '{topic_subject}' is already registered. Use overwrite=True to replace.")

        self._topic_schemas[topic_subject] = schema
        log.info(f"Registered schema '{schema.__name__}' for topic '{topic_subject}'.")
        # TODO: Integrate with external schema registry if client is available.

    def get_schema_for_topic(self, topic_subject: str) -> Optional[Type[BaseModel]]:
        """
        Retrieves the Pydantic schema for a given topic subject.

        Args:
            topic_subject: The NATS subject string.

        Returns:
            The Pydantic BaseModel class, or None if not registered.
        """
        return self._topic_schemas.get(topic_subject)

    def list_managed_topics(self) -> List[str]:
        """
        Returns a list of all topic subjects managed by this instance.

        Returns:
            A list of topic subject strings.
        """
        return list(self._topic_schemas.keys())

    def clear_all_registrations(self) -> None:
        """
        Removes all topic registrations from the manager.
        """
        self._topic_schemas.clear()
        log.info("All topic schema registrations have been cleared.")

    # --- Placeholder for Access Control ---

    def add_access_rule(self, topic: str, role: str, action: str) -> None:
        """
        Placeholder for adding an access control rule.

        Args:
            topic: The topic subject (can include wildcards).
            role: The role that is granted access (e.g., 'publisher', 'subscriber').
            action: The action being permitted (e.g., 'publish', 'subscribe').
        """
        log.warning("Access control is not fully implemented. This is a placeholder.")
        # Example structure: self._access_control_rules[topic] = {'role': 'action'}
        if topic not in self._access_control_rules:
            self._access_control_rules[topic] = []
        self._access_control_rules[topic].append({'role': role, 'action': action})

    def is_access_allowed(self, topic: str, role: str, action: str) -> bool:
        """
        Placeholder for checking access permissions for a topic.

        This method should implement logic to check against defined ACLs.
        For now, it returns True to allow all actions.

        Args:
            topic: The specific topic subject.
            role: The role of the client trying to perform an action.
            action: The action being attempted.

        Returns:
            True if access is permitted, False otherwise.
        """
        # TODO: Implement real access control logic.
        # This would involve matching the topic against wildcard rules,
        # checking the role, and verifying the action.
        if not self._access_control_rules:
            return True # Default to allow if no rules are set.

        # A very basic check for an exact match. A real implementation would be more complex.
        if topic in self._access_control_rules:
            for rule in self._access_control_rules[topic]:
                if rule['role'] == role and rule['action'] == action:
                    return True

        log.warning(f"Access check for topic '{topic}' is a placeholder and may not be secure.")
        return True # Defaulting to permissive for now.
