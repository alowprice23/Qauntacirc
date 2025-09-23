import numpy as np
from scipy.linalg import eigh
from . import laplacian as lap

def get_adjacency_spectrum(adj_matrix):
    """
    Computes the eigenvalue decomposition of an adjacency matrix.

    Args:
        adj_matrix (np.ndarray): The adjacency matrix of the graph.

    Returns:
        np.ndarray: The eigenvalues of the adjacency matrix.
        np.ndarray: The eigenvectors of theadjacency matrix.
    """
    if adj_matrix.shape[0] != adj_matrix.shape[1]:
        raise ValueError("Adjacency matrix must be square.")

    eigenvalues, eigenvectors = eigh(adj_matrix)
    return eigenvalues, eigenvectors

def analyze_connectivity(laplacian_matrix):
    """
    Analyzes the connectivity of a graph using its Laplacian spectrum.

    The number of zero eigenvalues of the Laplacian matrix corresponds to the
    number of connected components in the graph. The second smallest eigenvalue
    (Fiedler value) indicates how well the graph is connected.

    Args:
        laplacian_matrix (np.ndarray): The Laplacian matrix of the graph.

    Returns:
        int: The number of connected components.
        float: The algebraic connectivity (Fiedler value).
    """
    eigenvalues = np.sort(eigh(laplacian_matrix, eigvals_only=True))

    # Count zero eigenvalues (with a tolerance)
    num_components = np.sum(np.isclose(eigenvalues, 0))

    # Fiedler value (algebraic connectivity)
    fiedler_value = eigenvalues[1] if len(eigenvalues) > 1 else 0.0

    return num_components, fiedler_value

def spectral_clustering(adj_matrix, num_clusters):
    """
    Performs the initial steps of spectral clustering on a graph.

    This function computes the normalized eigenvectors of the graph Laplacian
    that are used for spectral clustering. The final clustering step (e.g., using
    K-Means) should be performed on the output of this function.

    Args:
        adj_matrix (np.ndarray): The adjacency matrix of the graph.
        num_clusters (int): The number of clusters to form.

    Returns:
        np.ndarray: An array of shape (n_nodes, n_clusters) containing the
                    normalized eigenvectors to be used for clustering.
    """
    L_sym = lap.get_normalized_laplacian(adj_matrix, form='sym')

    # Get the eigenvectors corresponding to the smallest eigenvalues
    eigenvalues, eigenvectors = eigh(L_sym)

    # Note: Sorting is implicitly handled by eigh for Hermitian matrices
    U = eigenvectors[:, :num_clusters]

    # Normalize the rows to have unit length
    with np.errstate(divide='ignore', invalid='ignore'):
        U_norm = U / np.linalg.norm(U, axis=1, keepdims=True)
        U_norm = np.nan_to_num(U_norm) # Handle cases with zero-norm rows

    return U_norm

def get_graph_energy(adj_matrix):
    """
    Computes the energy of a graph, defined as the sum of the absolute values
    of the eigenvalues of its adjacency matrix.

    Args:
        adj_matrix (np.ndarray): The adjacency matrix of the graph.

    Returns:
        float: The graph energy.
    """
    eigenvalues = eigh(adj_matrix, eigvals_only=True)
    return np.sum(np.abs(eigenvalues))

class SpectralAnalysis:
    """
    Provides spectral analysis of graphs.
    """
    def __init__(self, laplacian_matrix: np.ndarray):
        self.laplacian = laplacian_matrix

    def get_connectivity(self) -> (int, float):
        """
        Analyzes the connectivity of a graph using its Laplacian spectrum.
        """
        return analyze_connectivity(self.laplacian)

    def get_fiedler_value(self) -> float:
        """
        Returns the Fiedler value (algebraic connectivity).
        """
        _, fiedler_value = self.get_connectivity()
        return fiedler_value
