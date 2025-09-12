import pytest
from memory.types import Fact, FactType, Knowledge

def test_fact_creation():
    """Tests that a Fact object can be created."""
    fact_content = "The sky is blue."
    fact = Fact(
        content=fact_content,
        type=FactType.PROPOSITION,
        confidence=0.99
    )
    assert fact.content == fact_content
    assert fact.type == FactType.PROPOSITION
    assert fact.confidence == 0.99
    assert isinstance(fact, Knowledge)
