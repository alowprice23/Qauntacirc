import numpy as np
from scipy.linalg import eig, expm

class DiscreteTimeMarkovChain:
    """
    Represents a discrete-time Markov chain.
    """
    def __init__(self, transition_matrix):
        if not np.allclose(np.sum(transition_matrix, axis=1), 1):
            raise ValueError("Rows of the transition matrix must sum to 1.")
        self.P = transition_matrix
        self.n_states = transition_matrix.shape[0]

    def get_stationary_distribution(self):
        """
        Computes the stationary distribution of the Markov chain.
        The stationary distribution pi satisfies pi * P = pi.
        This is equivalent to finding the eigenvector of P.T with eigenvalue 1.
        """
        eigenvalues, eigenvectors = eig(self.P.T)

        # Find the eigenvector corresponding to the eigenvalue 1
        one_eig_idx = np.isclose(eigenvalues, 1)
        if not np.any(one_eig_idx):
            raise ValueError("No stationary distribution found (no eigenvalue of 1).")

        stationary_vector = eigenvectors[:, one_eig_idx].real.flatten()

        # Normalize to get a probability distribution
        return stationary_vector / np.sum(stationary_vector)

    def is_reversible(self, pi):
        """
        Checks if the Markov chain is reversible with respect to a distribution pi.
        This is the detailed balance condition: pi_i * P_ij = pi_j * P_ji.

        Args:
            pi (np.ndarray): A probability distribution.

        Returns:
            bool: True if the chain is reversible, False otherwise.
        """
        for i in range(self.n_states):
            for j in range(self.n_states):
                if not np.isclose(pi[i] * self.P[i, j], pi[j] * self.P[j, i]):
                    return False
        return True

    def mixing_time_bound(self):
        """
        Estimates an upper bound on the mixing time using the spectral gap.
        """
        # We need the eigenvalues of (P + P.T)/2 for a symmetric chain,
        # or other more complex bounds for non-symmetric chains.
        # Here's a simplified version for reversible chains.

        pi = self.get_stationary_distribution()
        if not self.is_reversible(pi):
            # This bound is simpler for reversible chains.
            # For non-reversible chains, other norms are needed.
            return "Mixing time bound not implemented for non-reversible chains."

        eigenvalues = np.sort(np.abs(eig(self.P, left=None, right=False)))

        # Spectral gap
        if len(eigenvalues) < 2:
            return np.inf

        spectral_gap = 1 - eigenvalues[-2] # Second largest eigenvalue magnitude

        if spectral_gap <= 0:
            return np.inf

        # A rough upper bound on mixing time
        return 1 / spectral_gap


class ContinuousTimeMarkovChain:
    """
    Represents a continuous-time Markov process.
    """
    def __init__(self, generator_matrix):
        if not np.allclose(np.sum(generator_matrix, axis=1), 0):
            raise ValueError("Rows of the generator matrix must sum to 0.")
        self.Q = generator_matrix
        self.n_states = generator_matrix.shape[0]

    def get_transition_matrix_at_t(self, t):
        """
        Computes the transition matrix P(t) = exp(tQ).

        Args:
            t (float): The time duration.

        Returns:
            np.ndarray: The transition matrix P(t).
        """
        return expm(t * self.Q)

    def get_stationary_distribution(self):
        """
        Computes the stationary distribution pi, which satisfies pi * Q = 0.
        """
        # This is equivalent to the DTMC case for the embedded chain,
        # but can also be solved directly.
        # For simplicity, we can use the same method as the DTMC.
        # A proper way would be to solve the linear system pi*Q=0, sum(pi)=1.

        # A simple approach:
        A = np.vstack((self.Q.T, np.ones(self.n_states)))
        b = np.zeros(self.n_states + 1)
        b[-1] = 1

        pi, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        return pi
