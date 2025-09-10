from __future__ import annotations
import numpy as np
from collections import Counter
from typing import List, Any

def shannon_entropy(data: List[Any] | np.ndarray) -> float:
    """
    Calculates the Shannon entropy of a list of data points or a probability distribution.

    H(X) = -Σᵢ p(xᵢ) log₂(p(xᵢ))

    Args:
        data: A list of data points or a numpy array representing a probability distribution.

    Returns:
        The Shannon entropy of the data in bits.
    """
    if isinstance(data, np.ndarray):
        prob_dist = data[data > 0]
        return -np.sum(prob_dist * np.log2(prob_dist))

    if not data:
        return 0.0

    n = len(data)
    counts = Counter(data)

    entropy = 0.0
    for count in counts.values():
        p_x = count / n
        if p_x > 0:
            entropy -= p_x * np.log2(p_x)

    return entropy

def mutual_information(joint_prob_dist):
    """
    Calculates the mutual information between two random variables from their
    joint probability distribution.

    I(X;Y) = H(X) + H(Y) - H(X,Y)

    Args:
        joint_prob_dist (np.ndarray): A 2D array representing the joint probability dist.

    Returns:
        float: The mutual information in bits.
    """
    joint_prob_dist = np.asarray(joint_prob_dist)
    p_x = np.sum(joint_prob_dist, axis=1)
    p_y = np.sum(joint_prob_dist, axis=0)

    h_x = shannon_entropy(p_x)
    h_y = shannon_entropy(p_y)
    h_xy = shannon_entropy(joint_prob_dist.flatten())

    return h_x + h_y - h_xy

def kl_divergence(p, q):
    """
    Calculates the Kullback-Leibler (KL) divergence between two probability distributions.

    D_KL(P || Q) = sum(p(x) * log2(p(x) / q(x)))

    Args:
        p (np.ndarray): The true probability distribution.
        q (np.ndarray): The approximate probability distribution.

    Returns:
        float: The KL divergence in bits.
    """
    p = np.asarray(p)
    q = np.asarray(q)

    # Remove entries where p is zero
    non_zero_p = p > 0
    p = p[non_zero_p]
    q = q[non_zero_p]

    # Avoid division by zero in q
    q[q == 0] = 1e-12

    return np.sum(p * np.log2(p / q))

def cross_entropy(p, q):
    """
    Calculates the cross-entropy between two probability distributions.

    H(P, Q) = - sum(p(x) * log2(q(x)))

    Args:
        p (np.ndarray): The true probability distribution.
        q (np.ndarray): The predicted probability distribution.

    Returns:
        float: The cross-entropy in bits.
    """
    p = np.asarray(p)
    q = np.asarray(q)

    # Avoid log(0)
    q[q == 0] = 1e-12

    return -np.sum(p * np.log2(q))
