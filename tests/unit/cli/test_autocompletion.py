import pytest
from unittest.mock import MagicMock, AsyncMock

from cli.autocompletion import (
    PhysicsBasedAutoCompletion,
    IntelligentCommandSuggester,
    PhysicsBasedPredictor,
    QuantumContext,
    CompletionSuggestions,
    SuggestionResult,
    PhysicsScore,
)
from memory.constellation import ConstellationMemory
from memory.types import Fact, FactType, ConstellationResult
from llm.client import LLMClient

@pytest.fixture
def mock_llm_client():
    client = MagicMock(spec=LLMClient)
    client.complete = MagicMock(return_value={"response": '{"suggestion": "suggested command"}'})
    return client

@pytest.fixture
def mock_constellation():
    constellation = MagicMock(spec=ConstellationMemory)
    # Mock the synchronous query_facts method
    # Create a realistic, dictionary-based FactNode to satisfy Pydantic validation
    fact_content = {"energy_delta": -10.0}
    fact = Fact(
        type=FactType.PATTERN,
        content="historical command",
        mathematical_properties=fact_content,
        confidence=0.9
    )

    optimal_encoding = {"algorithm": "none", "compressed_data": b"", "compression_ratio": 1.0, "entropy": 0.0, "bound_verification": {}, "optimality_proof": {}, "hash": "dummy_hash"}

    import numpy as np
    fact_node_dict = {
        "id": "fact1",
        "fact": fact.model_dump(),
        "encoding": optimal_encoding,
        "embedding": np.array([0.1, 0.2]), # Dummy embedding
        "storage_locations": {},
        "mathematical_certificate": "dummy_cert"
    }

    constellation.query_facts = MagicMock(return_value=ConstellationResult(
        facts=[fact_node_dict],
        query_hash="dummy_hash",
        mathematical_consistency={},
        information_content=1.0,
        retrieval_proof="dummy_proof"
    ))
    return constellation

@pytest.mark.asyncio
async def test_intelligent_command_suggester(mock_llm_client):
    # Arrange
    suggester = IntelligentCommandSuggester(mock_llm_client)
    partial_input = "partial"
    mock_pattern = MagicMock(spec=Fact)
    mock_pattern.content = "historical command"
    mock_pattern.confidence = 0.9
    mock_pattern.mathematical_properties = {"energy_delta": -10.0}
    quantum_context = QuantumContext(current_energy=100.0, phase="B")

    # Act
    result = await suggester.generate_suggestion(partial_input, mock_pattern, quantum_context)

    # Assert
    assert isinstance(result, SuggestionResult)
    assert result.text == "suggested command"
    assert result.confidence == 0.9
    assert result.predicted_energy_delta == -10.0

def test_physics_based_predictor():
    # Arrange
    predictor = PhysicsBasedPredictor()
    mock_suggestion = SuggestionResult(text="suggestion", confidence=0.9, predicted_energy_delta=-10.0)

    # Act
    score = predictor.compute_suggestion_score(mock_suggestion, 100.0, "B")

    # Assert
    assert isinstance(score, PhysicsScore)
    assert score.value > 0

@pytest.mark.asyncio
async def test_physics_based_autocompletion(mock_constellation, mock_llm_client):
    # Arrange
    autocompletion = PhysicsBasedAutoCompletion(mock_constellation, mock_llm_client)

    partial_input = "partial"
    quantum_context = QuantumContext(current_energy=100.0, phase="B")

    # Act
    result = await autocompletion.provide_intelligent_completion(partial_input, quantum_context)

    # Assert
    assert isinstance(result, CompletionSuggestions)
    assert len(result.suggestions) > 0
    assert result.suggestions[0].text == "suggested command"
    assert result.suggestions[0].physics_score > 0
