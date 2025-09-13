import pytest
from datetime import datetime

from memory.constellation import ConstellationMemory, InconsistentKnowledgeError
from memory.types import Fact, FactType, ConstellationQuery, Intent, Plan, ExecutionResult

def test_store_inconsistent_fact(constellation_memory: ConstellationMemory):
    """Tests that storing an inconsistent fact raises an error."""
    fact1 = Fact(type=FactType.PROPOSITION, content="A is B", timestamp=datetime(2023,1,1))
    constellation_memory.store_fact(fact1)

    fact2 = Fact(type=FactType.PROPOSITION, content="A is not B", timestamp=datetime(2023,1,1))
    with pytest.raises(InconsistentKnowledgeError):
        constellation_memory.store_fact(fact2)

def test_query_facts(constellation_memory: ConstellationMemory):
    """Tests querying for facts."""
    fact1 = Fact(type=FactType.PROPOSITION, content="The sun is a star.")
    constellation_memory.store_fact(fact1)

    fact2 = Fact(type=FactType.PROPOSITION, content="The moon is a satellite.")
    constellation_memory.store_fact(fact2)

    query = ConstellationQuery(text="star")
    results = constellation_memory.query_facts(query)

    assert len(results.facts) > 0
    # Check if the expected fact is in the results, not necessarily at the first position
    found_sun_fact = any("sun" in f.fact.content.lower() for f in results.facts)
    assert found_sun_fact

def test_learn_pattern(constellation_memory: ConstellationMemory):
    """Tests learning a new pattern."""
    intent = Intent(description="Test intent")
    plan = Plan(steps=["step 1", "step 2"])
    result = ExecutionResult(
        success=True,
        confidence=0.9,
        success_metrics={"success_rate": 0.95},
        energy_delta=-10,
        convergence_metrics={}
    )

    learning_result = constellation_memory.learn_pattern(intent, plan, result)

    assert learning_result.pattern_node is not None
    assert learning_result.pattern_node.fact.type == FactType.PATTERN
    assert learning_result.pattern_node.fact.content["intent"] == "Test intent"
    assert learning_result.learning_confidence is not None

def test_full_persistence_cycle(tmp_path):
    """Tests a full persist and restore cycle with a populated memory."""
    from memory.persistence import DurableMemoryStore
    from memory.types import ConstellationConfig

    config = ConstellationConfig(
        neo4j_uri="bolt://localhost:7687",
        embedding_dimension=4,
        database_path=str(tmp_path / "test.db")
    )
    memory = ConstellationMemory(config)
    memory_store = DurableMemoryStore(storage_path=tmp_path)

    # Add some data
    fact1 = Fact(type=FactType.PROPOSITION, content="This is fact number one")
    memory.store_fact(fact1)

    # Persist
    persistence_result = memory_store.persist_memory_state(memory)
    assert persistence_result.success

    # Restore
    restored_memory = memory_store.restore_memory_state(persistence_result.backup_id, ConstellationMemory)

    # Verify
    assert isinstance(restored_memory, ConstellationMemory)
    assert restored_memory.vector_store.index.ntotal == 1
    assert len(restored_memory._internal_knowledge_graph.nodes) == 1

    # Query the restored memory
    query = ConstellationQuery(text="fact number one")
    results = restored_memory.query_facts(query)
    assert len(results.facts) > 0
    assert results.facts[0].fact.content == "This is fact number one"
