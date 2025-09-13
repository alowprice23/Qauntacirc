import pytest
import numpy as np
from memory.encoder import ShannonEntropyCalculator, InformationTheoreticEncoder
from memory.types import Fact, FactType

@pytest.fixture
def encoder():
    """Provides an InformationTheoreticEncoder instance for testing."""
    return InformationTheoreticEncoder()

def test_shannon_entropy_calculator():
    """Tests the ShannonEntropyCalculator."""
    calculator = ShannonEntropyCalculator()

    # Test with empty data
    assert calculator.compute(b"") == 0.0

    # Test with uniform data (1 byte type) -> entropy should be 0
    assert calculator.compute(b"aaaa") == 0.0

    # Test with 2 byte types, equal probability -> entropy should be 1.0
    assert np.isclose(calculator.compute(b"abab"), 1.0)

    # Test with 4 byte types, equal probability -> entropy should be 2.0
    assert np.isclose(calculator.compute(b"abcd"), 2.0)

def test_optimality_proof(encoder: InformationTheoreticEncoder):
    """Tests the generation of the optimality proof."""
    fact = Fact(
        content="This is a test fact for checking the optimality proof.",
        type=FactType.PROPOSITION
    )
    encoding = encoder.encode(fact)

    proof = encoding.optimality_proof
    assert "optimal_algorithm" in proof
    assert "reason" in proof
    assert "results" in proof
    assert len(proof["results"]) == len(encoder.compression_algorithms)
    assert encoding.algorithm in proof["results"]

def test_compression_bound_verification(encoder: InformationTheoreticEncoder):
    """Tests the compression bound verification."""
    # Create a fact with highly random (less compressible) content
    random_content = np.random.bytes(1024)
    fact = Fact(content=random_content.decode('latin1'), type=FactType.PROPOSITION)

    encoding = encoder.encode(fact)

    # For random data, compression is not very effective, but the bound should still be reasonable
    verification = encoding.bound_verification
    assert "verified" in verification
    assert "theoretical_limit_bytes" in verification
    assert verification["theoretical_limit_bytes"] > 0

def test_best_algorithm_is_chosen(encoder: InformationTheoreticEncoder):
    """Tests that the encoder chooses the algorithm with the smallest size."""
    fact = Fact(
        content="Some repetitive content that should compress well with some algorithms.",
        type=FactType.PROPOSITION
    )
    encoding = encoder.encode(fact)

    proof = encoding.optimality_proof
    results = proof["results"]

    # Find the size of the chosen algorithm's output
    chosen_size = results[encoding.algorithm]["size"]

    # Verify that no other algorithm produced a smaller output
    for alg, res in results.items():
        assert res["size"] >= chosen_size
