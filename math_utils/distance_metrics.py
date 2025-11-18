import numpy as np
from scipy.spatial.distance import minkowski, directed_hausdorff
from scipy.stats import wasserstein_distance

def euclidean_distance(u, v):
    """Computes the Euclidean distance between two vectors."""
    return minkowski(u, v, p=2)

def manhattan_distance(u, v):
    """Computes the Manhattan distance between two vectors."""
    return minkowski(u, v, p=1)

def minkowski_distance(u, v, p):
    """Computes the Minkowski distance between two vectors."""
    return minkowski(u, v, p=p)

def levenshtein_distance(s1, s2):
    """
    Computes the Levenshtein (edit) distance between two sequences.
    This is useful for comparing code structures represented as strings.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def wasserstein_1d_distance(u_values, v_values):
    """
    Computes the 1D Wasserstein distance (Earth Mover's Distance) between two distributions.

    Args:
        u_values (np.ndarray): A 1D array of values from the first distribution.
        v_values (np.ndarray): A 1D array of values from the second distribution.

    Returns:
        float: The 1D Wasserstein distance.
    """
    return wasserstein_distance(u_values, v_values)

def hausdorff_distance(u, v):
    """
    Computes the Hausdorff distance between two sets of points.

    The Hausdorff distance is the maximum of the directed Hausdorff distances.

    Args:
        u (np.ndarray): A 2D array of points (N_u x D).
        v (np.ndarray): A 2D array of points (N_v x D).

    Returns:
        float: The Hausdorff distance.
    """
    d_uv = directed_hausdorff(u, v)[0]
    d_vu = directed_hausdorff(v, u)[0]
    return max(d_uv, d_vu)

def software_similarity_metric(state1, state2, weights=None):
    """
    A custom, composite similarity metric for software states.
    This is a placeholder for a domain-specific metric.

    Args:
        state1 (dict): A dictionary representing the first software state.
        state2 (dict): A dictionary representing the second software state.
        weights (dict): Weights for different components of the state.

    Returns:
        float: A composite distance score.
    """
    if weights is None:
        weights = {'code_structure': 0.6, 'dependencies': 0.4}

    # Example: comparing code structure using edit distance
    code_dist = levenshtein_distance(state1.get('code_str', ''), state2.get('code_str', ''))

    # Example: comparing dependency vectors using Euclidean distance
    dep_dist = euclidean_distance(state1.get('dep_vector', []), state2.get('dep_vector', []))

    # Normalize (this is highly simplified)
    norm_code_dist = code_dist / max(len(state1.get('code_str', '')), len(state2.get('code_str', '')))
    norm_dep_dist = dep_dist # Assuming vectors are already normalized

    return weights['code_structure'] * norm_code_dist + weights['dependencies'] * norm_dep_dist
