import pytest
from memory.encoder import InformationTheoreticEncoder
from memory.types import Fact, FactType

@pytest.fixture
def encoder():
    """Provides an InformationTheoreticEncoder instance for testing."""
    return InformationTheoreticEncoder()

def test_encode_fact(encoder: InformationTheoreticEncoder):
    """Tests encoding a fact."""
    fact = Fact(
        content="This is a test fact for encoding.",
        type=FactType.PROPOSITION
    )

    encoding = encoder.encode(fact)

    assert encoding.algorithm in encoder.compression_algorithms
    assert isinstance(encoding.compressed_data, bytes)
    assert encoding.compression_ratio > 0
    assert len(encoding.hash) == 64 # SHA256
