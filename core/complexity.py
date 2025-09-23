from math_utils.kolmogorov_bounds import KolmogorovApproximator
from math_utils.info_entropy import shannon_entropy

class ComplexityCalculator:
    """
    Calculates complexity using a combination of Kolmogorov complexity approximation
    and Shannon entropy for semantic features.
    """
    def __init__(self):
        self.kolmogorov_approximator = KolmogorovApproximator()

    def calculate(self, code: str, tokens: list[str]) -> float:
        """
        Calculates the complexity energy of a piece of code.
        E_complexity = K_approx(code) + H(tokens)
        """
        # Approximate Kolmogorov complexity
        k_approx = self.kolmogorov_approximator.approximate(code)

        # Calculate Shannon entropy of the code's tokens
        h_semantic = shannon_entropy(tokens)

        # The complexity energy is a combination of these two measures
        return float(k_approx + h_semantic)
