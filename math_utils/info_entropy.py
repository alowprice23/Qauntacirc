import numpy as np

def shannon_entropy(prob_dist):
    """
    Calculates the Shannon entropy of a probability distribution.

    H(X) = - sum(p(x) * log2(p(x)))

    Args:
        prob_dist (np.ndarray): A 1D array representing the probability distribution.

    Returns:
        float: The Shannon entropy in bits.
    """
    prob_dist = np.asarray(prob_dist)
    prob_dist = prob_dist[prob_dist > 0] # Remove zero probabilities
    return -np.sum(prob_dist * np.log2(prob_dist))

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
