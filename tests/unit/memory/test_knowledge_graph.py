import pytest
from memory.knowledge_graph import QuantumKnowledgeGraph
from memory.types import Knowledge, Relationship, RelationshipType

@pytest.fixture
def knowledge_graph():
    """Provides a QuantumKnowledgeGraph instance for testing."""
    return QuantumKnowledgeGraph()

def test_create_node(knowledge_graph: QuantumKnowledgeGraph):
    """Tests creating a knowledge node."""
    knowledge = Knowledge(content="Socrates is a man.")
    node = knowledge_graph.create_knowledge_node(knowledge)

    assert node.id in knowledge_graph.nodes
    assert knowledge_graph.nodes[node.id].knowledge.content == "Socrates is a man."

def test_create_edge(knowledge_graph: QuantumKnowledgeGraph):
    """Tests creating an edge between two nodes."""
    k1 = Knowledge(content="Socrates is a man.")
    n1 = knowledge_graph.create_knowledge_node(k1)

    k2 = Knowledge(content="All men are mortal.")
    n2 = knowledge_graph.create_knowledge_node(k2)

    relationship = Relationship(type=RelationshipType.IMPLIES)

    edge = knowledge_graph.create_knowledge_edge(n1.id, n2.id, relationship)

    assert edge.id in knowledge_graph.edges
    assert edge.source_id == n1.id
    assert edge.target_id == n2.id
    assert edge.relationship.type == RelationshipType.IMPLIES
