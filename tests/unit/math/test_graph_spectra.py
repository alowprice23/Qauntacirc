import pytest
import numpy as np
import networkx as nx
from math_utils.graph_spectra import (
    get_adjacency_spectrum,
    analyze_connectivity,
    spectral_clustering,
    get_graph_energy
)
from math_utils import laplacian as lap

@pytest.fixture
def simple_graph():
    G = nx.path_graph(4) # 0-1-2-3
    return nx.to_numpy_array(G)

@pytest.fixture
def disconnected_graph():
    G = nx.path_graph(3)
    G.add_node(3) # Disconnected node
    return nx.to_numpy_array(G)

def test_get_adjacency_spectrum(simple_graph):
    eigenvalues, eigenvectors = get_adjacency_spectrum(simple_graph)
    assert len(eigenvalues) == 4
    assert eigenvectors.shape == (4, 4)
    # Check if eigenvectors are orthogonal
    assert np.allclose(eigenvectors.T @ eigenvectors, np.eye(4))

def test_analyze_connectivity_connected(simple_graph):
    laplacian_matrix = lap.get_combinatorial_laplacian(simple_graph)
    num_components, fiedler_value = analyze_connectivity(laplacian_matrix)
    assert num_components == 1
    assert fiedler_value > 0

def test_analyze_connectivity_disconnected(disconnected_graph):
    laplacian_matrix = lap.get_combinatorial_laplacian(disconnected_graph)
    num_components, fiedler_value = analyze_connectivity(laplacian_matrix)
    assert num_components == 2
    # For a disconnected graph, the second eigenvalue (Fiedler value) should be 0
    assert np.isclose(fiedler_value, 0)

def test_spectral_clustering(simple_graph):
    num_clusters = 2
    U = spectral_clustering(simple_graph, num_clusters)
    assert U.shape == (4, num_clusters)
    # The rows should be normalized
    row_norms = np.linalg.norm(U, axis=1)
    # Allow for zero rows if a node is isolated
    assert np.all(np.isclose(row_norms, 1.0) | np.isclose(row_norms, 0.0))

def test_get_graph_energy(simple_graph):
    energy = get_graph_energy(simple_graph)
    # For path graph P4, eigenvalues are approx {-1.618, -0.618, 0.618, 1.618}
    # Energy is sum of abs values, approx 2 * (1.618 + 0.618) = 4.472
    assert energy == pytest.approx(2 * (1.618 + 0.618), abs=1e-2)
