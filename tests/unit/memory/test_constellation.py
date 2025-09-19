import pytest
import numpy as np
from memory.constellation import ConstellationMemory, NodeType

@pytest.fixture
def memory():
    """Provides a clean ConstellationMemory instance for each test."""
    return ConstellationMemory()

def test_add_fact(memory: ConstellationMemory):
    """Test that a fact can be added to the memory."""
    fact_id = memory.add_fact("The sky is blue", NodeType.FACT, metadata={"source": "test"})

    assert fact_id in memory.node_index
    assert fact_id in memory.graph

    node = memory.node_index[fact_id]
    assert node.content == "The sky is blue"
    assert node.type == NodeType.FACT
    assert node.metadata["source"] == "test"
    assert node.embedding is not None

def test_query_facts_simple(memory: ConstellationMemory):
    """Test basic fact querying."""
    memory.add_fact("The grass is green", NodeType.FACT)
    memory.add_fact("The sun is bright", NodeType.FACT)

    results = memory.query_facts("bright sun", limit=1)
    assert len(results) == 1
    assert "sun is bright" in results[0].content

def test_query_facts_empty(memory: ConstellationMemory):
    """Test querying an empty memory."""
    results = memory.query_facts("anything")
    assert len(results) == 0

def test_similarity_inference(memory: ConstellationMemory):
    """Test that 'similar_to' relationships are inferred."""
    memory.add_fact("AI agents have the capability to reason about complex problems.", NodeType.FACT)
    memory.add_fact("AI agents can reason through complex problems and think.", NodeType.FACT)

    # Find the edge between the two nodes
    edges = list(memory.graph.edges(data=True))
    similar_edge = [d for u, v, d in edges if d.get("relation") == "similar_to"]

    assert len(similar_edge) > 0
    assert similar_edge[0]['weight'] > 0.7

def test_causality_inference(memory: ConstellationMemory):
    """Test that causal relationships are inferred."""
    memory.add_fact("High temperature causes ice", NodeType.FACT)
    memory.add_fact("Melted ice is water", NodeType.FACT)

    # Find the 'causes' edge
    edges = list(memory.graph.edges(data=True))
    causes_edge = [d for u, v, d in edges if d.get("relation") == "causes"]

    assert len(causes_edge) == 1
    assert causes_edge[0]['confidence'] == 0.8

def test_contradiction_inference(memory: ConstellationMemory):
    """Test that contradictions are inferred."""
    memory.add_fact("The system is stable", NodeType.FACT)
    memory.add_fact("The system is not stable", NodeType.FACT)

    # Find the 'contradicts' edge
    edges = list(memory.graph.edges(data=True))
    contradicts_edge = [d for u, v, d in edges if d.get("relation") == "contradicts"]

    assert len(contradicts_edge) > 0  # Can be 1 or 2 depending on order
    assert contradicts_edge[0]['confidence'] == 0.9

def test_get_context(memory: ConstellationMemory):
    """Test the get_context method."""
    memory.add_fact("The first law of thermodynamics is about energy conservation.", NodeType.FACT)
    # Add a very similar fact to ensure a relationship is created
    memory.add_fact("The first law of thermodynamics is about the conservation of energy.", NodeType.FACT)
    memory.add_fact("The second law of thermodynamics is about entropy.", NodeType.FACT)
    memory.add_fact("Entropy always increases in a closed system.", NodeType.FACT)

    context = memory.get_context("thermodynamics laws", max_tokens=200)
    assert "thermodynamics" in context
    assert "entropy" in context
    assert "Related" in context # Check if graph traversal part works

def test_generate_llm_context(memory: ConstellationMemory):
    """Test the generate_llm_context method."""
    memory.add_fact(
        "Agent-007 completed task 'analyze_market'",
        NodeType.FACT,
        metadata={"agent_id": "007"}
    )
    memory.add_fact(
        "Market analysis shows a downward trend",
        NodeType.DECISION,
        metadata={"status": "approved"}
    )

    context_data = memory.generate_llm_context(
        agent_id="007",
        current_task="Predict future market trends"
    )

    assert "formatted_context" in context_data
    assert "context_components" in context_data
    formatted_context = context_data["formatted_context"]

    assert "AGENT HISTORY" in formatted_context
    assert "Agent-007" in formatted_context
    assert "RELEVANT FACTS" in formatted_context
    assert "downward trend" in formatted_context
