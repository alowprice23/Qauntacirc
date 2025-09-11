"""
Comprehensive Tests for Topic Manager
Mathematical Foundation: Graph theory for routing, load balancing
Physics Principle: Network topology, routing optimization
What Gets Tested: Topic routing, load distribution
Failure Analysis: Diagnostic guidance for topic routing and management failures
"""

import pytest
from tests.conftest import TestDiagnostic
from pydantic import BaseModel

from messaging.topic_manager import TopicManager

class TestTopicManager:
    def test_topic_manager_import(self):
        diagnostic = TestDiagnostic(
            component_name="TopicManager",
            expected_behavior="The TopicManager module should be importable.",
            failure_indicators=["ImportError"],
            build_instructions=["Create the TopicManager in 'messaging/topic_manager.py'"],
            mathematical_requirements=["Graph-based routing for optimal load balancing"],
            acceptance_criteria={"import": "successful"},
            physics_principle="Network topology and routing optimization",
            related_components=["StreamManager"]
        )
        try:
            from messaging.topic_manager import TopicManager
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))

class DummySchema(BaseModel):
    field: str

def test_topic_registration_and_retrieval():
    """
    Tests that a topic schema can be registered and then retrieved.
    """
    manager = TopicManager()
    topic = "test.topic.schema"

    manager.register_topic(topic, DummySchema)

    retrieved_schema = manager.get_schema_for_topic(topic)
    assert retrieved_schema == DummySchema

    assert manager.list_managed_topics() == [topic]

def test_register_duplicate_topic_raises_error():
    """
    Tests that registering the same topic twice without overwrite=True raises an error.
    """
    manager = TopicManager()
    topic = "test.topic.duplicate"

    manager.register_topic(topic, DummySchema)

    with pytest.raises(ValueError):
        manager.register_topic(topic, DummySchema)

def test_register_duplicate_topic_with_overwrite():
    """
    Tests that registering the same topic twice with overwrite=True succeeds.
    """
    manager = TopicManager()
    topic = "test.topic.overwrite"

    class AnotherDummySchema(BaseModel):
        other_field: int

    manager.register_topic(topic, DummySchema)
    manager.register_topic(topic, AnotherDummySchema, overwrite=True)

    retrieved_schema = manager.get_schema_for_topic(topic)
    assert retrieved_schema == AnotherDummySchema
