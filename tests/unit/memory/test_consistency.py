import pytest
import numpy as np
from datetime import datetime

from memory.consistency import MathematicalConsistencyEngine, ContradictionDetector
from memory.knowledge_graph import QuantumKnowledgeGraph
from memory.types import Knowledge, Fact, FactType

@pytest.fixture
def consistency_engine():
    """Provides a MathematicalConsistencyEngine instance for testing."""
    return MathematicalConsistencyEngine()

@pytest.fixture
def knowledge_graph():
    """Provides a QuantumKnowledgeGraph instance for testing."""
    return QuantumKnowledgeGraph()

def test_contradiction_detector(knowledge_graph: QuantumKnowledgeGraph):
    """Tests the contradiction detector."""
    detector = ContradictionDetector()

    fixed_timestamp = datetime(2023, 1, 1)

    # Add a fact to the graph
    fact1 = Fact(type=FactType.PROPOSITION, content="The sky is blue.", timestamp=fixed_timestamp)
    knowledge_graph.create_knowledge_node(fact1)

    # Check for a contradiction
    fact2 = Fact(type=FactType.PROPOSITION, content="The sky is not blue.", timestamp=fixed_timestamp)
    result = detector.find_contradictions(fact2, knowledge_graph)

    assert len(result.contradictions) == 1
    assert "Contradiction found" in result.contradictions[0]

    # Check for no contradiction
    fact3 = Fact(type=FactType.PROPOSITION, content="The grass is green.", timestamp=fixed_timestamp)
    result = detector.find_contradictions(fact3, knowledge_graph)
    assert len(result.contradictions) == 0

def test_consistency_engine_with_contradiction(consistency_engine: MathematicalConsistencyEngine, knowledge_graph: QuantumKnowledgeGraph):
    """Tests the full consistency engine with a contradiction."""
    fixed_timestamp = datetime(2023, 1, 1)
    fact1 = Fact(type=FactType.PROPOSITION, content="Water is wet.", timestamp=fixed_timestamp)
    knowledge_graph.create_knowledge_node(fact1)

    fact2 = Fact(type=FactType.PROPOSITION, content="Water is not wet.", timestamp=fixed_timestamp)

    result = consistency_engine.verify_consistency(fact2, knowledge_graph)

    assert not result.consistent
    assert len(result.violations) == 1
    assert "Contradiction found" in result.violations[0]
    assert result.suggested_resolution is not None

def test_consistency_engine_no_contradiction(consistency_engine: MathematicalConsistencyEngine, knowledge_graph: QuantumKnowledgeGraph):
    """Tests the full consistency engine with no contradiction."""
    fact1 = Fact(type=FactType.PROPOSITION, content="The sun is hot.")
    knowledge_graph.create_knowledge_node(fact1)

    fact2 = Fact(type=FactType.PROPOSITION, content="The moon is cold.")

    result = consistency_engine.verify_consistency(fact2, knowledge_graph)

    assert result.consistent
    assert len(result.violations) == 0
    assert result.proof is not None

def test_semantic_validator_with_relationships(knowledge_graph: QuantumKnowledgeGraph):
    """
    Tests the semantic validator logic.
    Note: The current implementation of SemanticValidator is a placeholder.
    This test is designed to be extended when the logic is implemented.
    """
    from memory.consistency import SemanticValidator
    validator = SemanticValidator(similarity_threshold=0.8)

    # In the current structure, semantic validation is called on a single knowledge piece.
    # A more realistic scenario would be to validate a new relationship.
    # For now, we just test the placeholder.

    k1 = Knowledge(content="A car is a vehicle.")
    result = validator.validate_semantics(k1, knowledge_graph)
    assert result.valid

# This test is for the logical rule engine, which is also a placeholder.
def test_logical_rule_engine(knowledge_graph: QuantumKnowledgeGraph):
    """
    Tests the logical rule engine.
    Note: The current implementation is a placeholder.
    """
    from memory.consistency import LogicalRuleEngine
    engine = LogicalRuleEngine()

    k1 = Knowledge(content="A implies B")
    result = engine.check_consistency(k1, knowledge_graph)
    assert result.valid
