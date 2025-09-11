"""
Comprehensive Tests for Message Serialization
Mathematical Foundation: Lossless compression, encoding efficiency
Physics Principle: Information encoding, compression theory
What Gets Tested: Serialization accuracy, compression effectiveness
Failure Analysis: Diagnostic guidance for serialization and compression failures
"""

import pytest
from tests.conftest import TestDiagnostic
from pydantic import BaseModel
import zlib

from messaging.serialization import MessageSerializer, SerializationFormat

class TestSerialization:
    def test_serialization_import(self):
        diagnostic = TestDiagnostic(
            component_name="Serialization",
            expected_behavior="The Serialization module should be importable.",
            failure_indicators=["ImportError"],
            build_instructions=["Create the Serialization functions in 'messaging/serialization.py'"],
            mathematical_requirements=["Lossless compression algorithms"],
            acceptance_criteria={"import": "successful"},
            physics_principle="Information encoding and compression theory",
            related_components=["Publisher", "Subscriber"]
        )
        try:
            from messaging.serialization import MessageSerializer
            serializer = MessageSerializer()
            serialize = serializer.serialize
            deserialize = serializer.deserialize
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))

class DummyModel(BaseModel):
    message: str
    value: int

def test_json_serialization_deserialization():
    """
    Tests that a Pydantic model can be serialized to JSON and back.
    """
    serializer = MessageSerializer()
    model = DummyModel(message="hello", value=42)

    serialized_data, is_compressed = serializer.serialize(model, format=SerializationFormat.JSON)

    assert not is_compressed
    assert isinstance(serialized_data, bytes)

    deserialized_model = serializer.deserialize(
        serialized_data,
        target_class=DummyModel,
        format=SerializationFormat.JSON,
        is_compressed=is_compressed
    )

    assert deserialized_model == model

def test_msgpack_serialization_deserialization():
    """
    Tests that a Pydantic model can be serialized to MessagePack and back.
    """
    serializer = MessageSerializer()
    model = DummyModel(message="hello", value=42)

    serialized_data, is_compressed = serializer.serialize(model, format=SerializationFormat.MSGPACK)

    assert not is_compressed
    assert isinstance(serialized_data, bytes)

    deserialized_model = serializer.deserialize(
        serialized_data,
        target_class=DummyModel,
        format=SerializationFormat.MSGPACK,
        is_compressed=is_compressed
    )

    assert deserialized_model == model

def test_compression_logic():
    """
    Tests that messages larger than the threshold are compressed.
    """
    # Threshold of 1 byte means any non-empty message should be compressed
    serializer = MessageSerializer(compress_threshold=1)
    model = DummyModel(message="a" * 1000, value=123) # a large message

    serialized_data, is_compressed = serializer.serialize(model, format=SerializationFormat.JSON)

    assert is_compressed

    # Verify that we can decompress and deserialize it
    deserialized_model = serializer.deserialize(
        serialized_data,
        target_class=DummyModel,
        format=SerializationFormat.JSON,
        is_compressed=is_compressed
    )

    assert deserialized_model == model
