import pytest
import numpy as np

from memory.knowledge_graph import QuantumKnowledgeGraph, InvalidRelationshipError
from memory.types import Knowledge, Relationship, RelationshipType, QueryConstraints

@pytest.fixture
def populated_graph():
    """Provides a QKG instance with some nodes and edges."""
    graph = QuantumKnowledgeGraph()
    k1 = Knowledge(content="Entity A")
    k2 = Knowledge(content="Entity B")
    k3 = Knowledge(content="Entity C")

    n1 = graph.create_knowledge_node(k1)
    n2 = graph.create_knowledge_node(k2)
    n3 = graph.create_knowledge_node(k3)

    rel1 = Relationship(type=RelationshipType.IMPLIES)
    rel2 = Relationship(type=RelationshipType.CAUSES, properties={"strength": 0.8})

    graph.create_knowledge_edge(n1.id, n2.id, rel1)
    graph.create_knowledge_edge(n2.id, n3.id, rel2)

    return graph, (n1, n2, n3)

def test_node_creation_is_deterministic(knowledge_graph: QuantumKnowledgeGraph):
    """Tests that creating a node with the same knowledge results in the same node."""
    k1 = Knowledge(content="Same content")
    node1 = knowledge_graph.create_knowledge_node(k1)
    node2 = knowledge_graph.create_knowledge_node(k1)
    assert node1.id == node2.id
    assert node1.access_count == 2
    assert np.array_equal(node1.embedding_vector, node2.embedding_vector)

def test_embedding_is_deterministic(knowledge_graph: QuantumKnowledgeGraph):
    """Tests that the embedding is deterministic for the same content."""
    k1 = Knowledge(content="Some knowledge content")
    k2 = Knowledge(content="Some knowledge content")
    k3 = Knowledge(content="Different knowledge content")

    emb1 = knowledge_graph._compute_embedding(k1)
    emb2 = knowledge_graph._compute_embedding(k2)
    emb3 = knowledge_graph._compute_embedding(k3)

    assert np.array_equal(emb1, emb2)
    assert not np.array_equal(emb1, emb3)

def test_adjacency_list_updates(populated_graph):
    """Tests if adjacency lists are updated correctly."""
    graph, (n1, n2, n3) = populated_graph
    assert n2.id in graph.adj[n1.id]
    assert n3.id in graph.adj[n2.id]
    assert n1.id in graph.rev_adj[n2.id]
    assert n2.id in graph.rev_adj[n3.id]

def test_relationship_validation(knowledge_graph: QuantumKnowledgeGraph):
    """Tests the validation of relationships."""
    k1 = Knowledge(content="Node 1")
    k2 = Knowledge(content="Node 2")
    n1 = knowledge_graph.create_knowledge_node(k1)
    n2 = knowledge_graph.create_knowledge_node(k2)

    # This relationship is invalid because it's missing the 'strength' property
    invalid_rel = Relationship(type=RelationshipType.CAUSES)
    with pytest.raises(InvalidRelationshipError):
        knowledge_graph.create_knowledge_edge(n1.id, n2.id, invalid_rel)

    # This relationship is valid
    valid_rel = Relationship(type=RelationshipType.CAUSES, properties={"strength": 0.9})
    edge = knowledge_graph.create_knowledge_edge(n1.id, n2.id, valid_rel)
    assert edge is not None

def test_traverse_knowledge_path(populated_graph):
    """Tests path traversal in the knowledge graph."""
    graph, (n1, n2, n3) = populated_graph

    # Test traversal from n1
    result = graph.traverse_knowledge_path(n1.id, QueryConstraints(max_depth=2))

    # Extract node IDs from the result paths for easier comparison
    result_path_ids = [[node.id for node in p] for p in result.paths]

    assert [n1.id] in result_path_ids
    assert [n1.id, n2.id] in result_path_ids
    assert len(result.paths) >= 2 # Check that we have at least the two expected paths.

def test_traverse_knowledge_path_deeper(populated_graph):
    """Tests deeper path traversal in the knowledge graph."""
    graph, (n1, n2, n3) = populated_graph

    # Test traversal from n1 with sufficient depth
    result = graph.traverse_knowledge_path(n1.id, QueryConstraints(max_depth=3))

    assert len(result.paths) == 3 # Should find [n1], [n1, n2], [n1, n2, n3]

    result_path_ids = [[node.id for node in p] for p in result.paths]

    assert [n1.id] in result_path_ids
    assert [n1.id, n2.id] in result_path_ids
    assert [n1.id, n2.id, n3.id] in result_path_ids

def test_path_ranking(knowledge_graph: QuantumKnowledgeGraph):
    """Tests if paths are ranked by information content."""
    k1 = Knowledge(content="High confidence", initial_confidence=1.0)
    k3 = Knowledge(content="Low confidence", initial_confidence=0.1)
    root_k = Knowledge(content="root", initial_confidence=0.9)

    n1 = knowledge_graph.create_knowledge_node(k1)
    n3 = knowledge_graph.create_knowledge_node(k3)
    root_n = knowledge_graph.create_knowledge_node(root_k)

    rel1 = Relationship(type=RelationshipType.IMPLIES)
    knowledge_graph.create_knowledge_edge(root_n.id, n1.id, rel1)
    knowledge_graph.create_knowledge_edge(root_n.id, n3.id, rel1)

    result = knowledge_graph.traverse_knowledge_path(root_n.id, QueryConstraints(max_depth=2))

    # Expected paths: [root], [root, n1], [root, n3]
    # Ranking should be based on avg confidence:
    # path_root_n1_info = (0.9 + 1.0) / 2 = 0.95
    # path_root_info = 0.9
    # path_root_n3_info = (0.9 + 0.1) / 2 = 0.5

    result_paths_ids = [[node.id for node in p] for p in result.paths]

    assert len(result_paths_ids) == 3
    assert [root_n.id] in result_paths_ids
    assert [root_n.id, n1.id] in result_paths_ids
    assert [root_n.id, n3.id] in result_paths_ids

    # Check the order
    # The _rank_paths_by_information_content sorts in descending order of info content
    def get_path_info(path_ids):
        return sum(knowledge_graph.nodes[node_id].confidence_score for node_id in path_ids) / len(path_ids)

    path_infos = [get_path_info(p) for p in result_paths_ids]

    # Assert that the list of info contents is sorted
    assert path_infos == sorted(path_infos, reverse=True)

    # Assert the specific order of paths based on their info content
    assert result_paths_ids[0] == [root_n.id, n1.id] # Highest info content
    assert result_paths_ids[1] == [root_n.id]
    assert result_paths_ids[2] == [root_n.id, n3.id] # Lowest info content
