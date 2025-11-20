import numpy as np
from scipy.linalg import eigh

def get_combinatorial_laplacian(adj_matrix):
    """
    Computes the combinatorial Laplacian of a graph.

    L = D - A, where D is the degree matrix and A is the adjacency matrix.

    Args:
        adj_matrix (np.ndarray): The adjacency matrix of the graph.

    Returns:
        np.ndarray: The combinatorial Laplacian matrix.
    """
    degree_matrix = np.diag(np.sum(adj_matrix, axis=1))
    return degree_matrix - adj_matrix

def get_normalized_laplacian(adj_matrix, form='sym'):
    """
    Computes the normalized Laplacian of a graph.

    Forms:
    - 'sym': L_sym = I - D^(-1/2) * A * D^(-1/2) (symmetric)
    - 'rw': L_rw = I - D^(-1) * A (random walk)

    Args:
        adj_matrix (np.ndarray): The adjacency matrix of the graph.
        form (str): The form of the normalized Laplacian ('sym' or 'rw').

    Returns:
        np.ndarray: The normalized Laplacian matrix.
    """
    degrees = np.sum(adj_matrix, axis=1)
<<<<<<< HEAD
<<<<<<< HEAD
    # To handle disconnected nodes, we only compute the inverse for non-zero degrees.
    inv_degrees = np.zeros_like(degrees, dtype=float)
    non_zero_mask = degrees > 0
    inv_degrees[non_zero_mask] = 1.0 / degrees[non_zero_mask]

    if form == 'sym':
        inv_sqrt_degrees = np.sqrt(inv_degrees)
        D_inv_sqrt = np.diag(inv_sqrt_degrees)
        I = np.identity(adj_matrix.shape[0])
        return I - D_inv_sqrt @ adj_matrix @ D_inv_sqrt
    elif form == 'rw':
        D_inv = np.diag(inv_degrees)
=======
=======
>>>>>>> remotes/origin/feat/core-infrastructure
    D_inv_sqrt = np.diag(1.0 / np.sqrt(degrees), where=degrees > 0)

    if form == 'sym':
        I = np.identity(adj_matrix.shape[0])
        return I - D_inv_sqrt @ adj_matrix @ D_inv_sqrt
    elif form == 'rw':
        D_inv = np.diag(1.0 / degrees, where=degrees > 0)
<<<<<<< HEAD
>>>>>>> remotes/origin/feat/core-infrastructure
=======
>>>>>>> remotes/origin/feat/core-infrastructure
        return np.identity(adj_matrix.shape[0]) - D_inv @ adj_matrix
    else:
        raise ValueError("Form must be 'sym' or 'rw'.")

def cheeger_constant(adj_matrix):
    """
    Estimates the Cheeger constant of a graph using the second smallest
    eigenvalue of the normalized Laplacian (Cheeger's inequality).

    h(G) approx= sqrt(2 * lambda_2)

    Args:
        adj_matrix (np.ndarray): The adjacency matrix of the graph.

    Returns:
        float: An estimate of the Cheeger constant.
    """
    L_sym = get_normalized_laplacian(adj_matrix, form='sym')
    eigenvalues = eigh(L_sym, eigvals_only=True)
    lambda_2 = eigenvalues[1] if len(eigenvalues) > 1 else 0
    return np.sqrt(2 * lambda_2)

def get_heat_kernel(adj_matrix, t):
    """
    Computes the graph heat kernel H_t = exp(-t * L).

    Args:
        adj_matrix (np.ndarray): The adjacency matrix of the graph.
        t (float): The time parameter.

    Returns:
        np.ndarray: The heat kernel matrix.
    """
    L = get_combinatorial_laplacian(adj_matrix)
    eigenvalues, eigenvectors = eigh(L)
    exp_diag = np.diag(np.exp(-t * eigenvalues))
    return eigenvectors @ exp_diag @ eigenvectors.T
