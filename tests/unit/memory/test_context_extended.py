import pytest
import numpy as np
from unittest.mock import MagicMock

from memory.context import ContextAssemblyEngine, InformationOptimizer
from memory.constellation import ConstellationMemory
from memory.types import (
    Fact, FactNode, OptimalEncoding, FactType,
    OptimizationProblem, OptimizationItem, TokenConstraint, AssembledContext
)

@pytest.fixture
def context_engine():
    """Provides a ContextAssemblyEngine with a mocked constellation."""
    mock_constellation = MagicMock(spec=ConstellationMemory)
    return ContextAssemblyEngine(constellation=mock_constellation)

def test_information_value_calculation(context_engine: ContextAssemblyEngine):
    """Tests the calculation of information value."""
    fact = Fact(content="High confidence, high entropy", type=FactType.PROPOSITION, confidence=0.9)
    encoding = OptimalEncoding(algorithm='zstd', compressed_data=b'', compression_ratio=0.5, entropy=4.0, bound_verification={}, optimality_proof="", hash="hash1")
    fact_node = FactNode(id="f1", fact=fact, encoding=encoding, embedding=np.array([]), storage_locations={})

    value = context_engine._compute_information_value(fact_node)

    # Expected value = 0.6 * 0.9 + 0.4 * 4.0 = 0.54 + 1.6 = 2.14
    assert np.isclose(value, 2.14)

def test_context_structure(context_engine: ContextAssemblyEngine):
    """Tests the structure of the assembled context."""
    fact1 = Fact(content="Fact 1 content", type=FactType.PROPOSITION, confidence=0.9, mathematical_properties={"prop": "val1"})
    fact2 = Fact(content="Fact 2 content", type=FactType.PATTERN, confidence=0.8, mathematical_properties={"prop": "val2"})

    assembled_context = context_engine._assemble_context_preserving_structure([fact1, fact2])

    assert "Type: PROPOSITION" in assembled_context.text
    assert "Type: PATTERN" in assembled_context.text
    assert "Content: Fact 1 content" in assembled_context.text
    assert "Properties: {'prop': 'val1'}" in assembled_context.text
    assert "Confidence: 0.90" in assembled_context.text

from datetime import datetime

def test_context_consistency_check(context_engine: ContextAssemblyEngine):
    """Tests the verification of context consistency."""
    fixed_timestamp = datetime(2023, 1, 1)

    # Consistent context
    fact1 = Fact(content="A is B", type=FactType.PROPOSITION, confidence=1.0, timestamp=fixed_timestamp)
    fact2 = Fact(content="C is D", type=FactType.PROPOSITION, confidence=1.0, timestamp=fixed_timestamp)
    good_context = AssembledContext(text="", selected_facts=[fact1, fact2])
    result = context_engine._verify_context_consistency(good_context)
    assert result["consistent"]

    # Inconsistent context
    fact3 = Fact(content="A is not B", type=FactType.PROPOSITION, confidence=1.0, timestamp=fixed_timestamp)
    bad_context = AssembledContext(text="", selected_facts=[fact1, fact3])
    result = context_engine._verify_context_consistency(bad_context)
    assert not result["consistent"]
    assert "Contradiction found" in result["violations"][0]

def test_information_optimizer():
    """Tests the information optimizer (knapsack solver)."""
    optimizer = InformationOptimizer()

    # Create dummy facts for the test
    fact1 = Fact(content="item1", type=FactType.PROPOSITION, confidence=1.0)
    fact2 = Fact(content="item2", type=FactType.PROPOSITION, confidence=1.0)
    fact3 = Fact(content="item3", type=FactType.PROPOSITION, confidence=1.0)

    # item1: value=10, weight=5, ratio=2.0
    # item2: value=12, weight=8, ratio=1.5
    # item3: value=8, weight=3, ratio=2.67
    item1 = OptimizationItem(id="1", value=10, weight=5, fact=fact1)
    item2 = OptimizationItem(id="2", value=12, weight=8, fact=fact2)
    item3 = OptimizationItem(id="3", value=8, weight=3, fact=fact3)

    problem = OptimizationProblem(
        objective="test",
        items=[item1, item2, item3],
        constraints=[TokenConstraint(max_tokens=10)],
        mathematical_formulation=""
    )

    solution = optimizer.solve(problem)

    # Greedy choice: item3 (ratio 2.67) + item1 (ratio 2.0)
    # Total weight = 3 + 5 = 8 <= 10. Total value = 8 + 10 = 18
    assert solution.total_information == 18

    selected_contents = [fact.content for fact in solution.selected_facts]
    assert "item1" in selected_contents
    assert "item3" in selected_contents
    assert len(solution.selected_facts) == 2
