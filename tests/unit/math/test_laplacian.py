import pytest
import numpy as np
import networkx as nx
from math_utils.laplacian import (
    get_combinatorial_laplacian,
    get_normalized_laplacian,
    cheeger_constant,
    get_heat_kernel
)

@pytest.fixture
def simple_graph():
    G = nx.path_graph(4) # 0-1-2-3
    return nx.to_numpy_array(G)

def test_get_combinatorial_laplacian(simple_graph):
    L = get_combinatorial_laplacian(simple_graph)
    # L = D - A
    D = np.diag([1, 2, 2, 1])
    A = simple_graph
    expected_L = D - A
    assert np.array_equal(L, expected_L)

def test_get_normalized_laplacian(simple_graph):
    L_sym = get_normalized_laplacian(simple_graph, form='sym')
    assert L_sym.shape == (4, 4)
    # Check for symmetry
    assert np.allclose(L_sym, L_sym.T)
    # Diagonal elements should be 1
    assert np.allclose(np.diag(L_sym), 1.0)

    L_rw = get_normalized_laplacian(simple_graph, form='rw')
    assert L_rw.shape == (4, 4)
    # Row sums should be 0
    assert np.allclose(np.sum(L_rw, axis=1), 0)

    with pytest.raises(ValueError):
        get_normalized_laplacian(simple_graph, form='invalid')

def test_cheeger_constant(simple_graph):
    # For a path graph, the Cheeger constant is known
    # For P4, h(G) = 1/2
    # Cheeger's inequality gives a bound, not the exact value.
    # We will test that the estimate is reasonable.
    h_estimate = cheeger_constant(simple_graph)
    assert h_estimate > 0
    # The second smallest eigenvalue of L_sym for P4 is 0.5.
    # h_estimate = sqrt(2 * 0.5) = 1.0
    assert h_estimate == pytest.approx(1.0)


def test_get_heat_kernel(simple_graph):
    t = 1.0
    H_t = get_heat_kernel(simple_graph, t)
    assert H_t.shape == (4, 4)
    # The heat kernel should be symmetric
    assert np.allclose(H_t, H_t.T)
    # The trace of the heat kernel is the sum of exp(-t*lambda_i)
    L = get_combinatorial_laplacian(simple_graph)
    eigenvalues = np.linalg.eigvalsh(L)
    expected_trace = np.sum(np.exp(-t * eigenvalues))
    assert np.trace(H_t) == pytest.approx(expected_trace)
