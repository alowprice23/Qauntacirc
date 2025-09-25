from risk.chernoff_bounds import chernoff_bound_verified_failure, chernoff_bound_empirical_failure

class RiskBudgetManager:
    """
    Manages the risk budget for the system, based on formal verification,
    empirical testing, and supply chain risk.
    """

    MAX_SYSTEM_FAILURE_PROB = 1.01e-4

    def __init__(self, n: int, epsilon: float, m: int, delta: float, p_s: float, rho_residual: float):
        """
        Initializes the RiskBudgetManager.

        Args:
            n: Number of verification runs (for P_v).
            epsilon: Error tolerance for formal verification (for P_v).
            m: Number of empirical tests (for P_e).
            delta: Error tolerance for empirical tests (for P_e).
            p_s: Probability of supply chain failure.
            rho_residual: Residual risk from empirical testing gaps.
        """
        if not all(isinstance(arg, (int, float)) and arg > 0 for arg in [n, epsilon, m, delta, p_s, rho_residual]):
            raise ValueError("All risk parameters must be positive numbers.")

        self.n = n
        self.epsilon = epsilon
        self.m = m
        self.delta = delta
        self.p_s = p_s
        self.rho_residual = rho_residual

    def calculate_verified_failure_prob(self) -> float:
        """
        Calculates P_v, the probability of verified failure.
        P(verified failure) ≤ 2exp(-2nε²)
        """
        return chernoff_bound_verified_failure(self.n, self.epsilon)

    def calculate_empirical_failure_prob(self) -> float:
        """
        Calculates P_e, the probability of empirical failure.
        P(empirical failure) ≤ 2exp(-2mδ²) + ρ_residual
        """
        return chernoff_bound_empirical_failure(self.m, self.delta) + self.rho_residual

    def calculate_total_system_failure_prob(self) -> float:
        """
        Calculates the composite system failure probability.
        P(system failure) ≤ P_v + P_e + P_s
        """
        p_v = self.calculate_verified_failure_prob()
        p_e = self.calculate_empirical_failure_prob()
        return p_v + p_e + self.p_s

    def is_within_budget(self) -> bool:
        """
        Checks if the total system failure probability is within the acceptable budget.
        P(system failure) ≤ 1.01 × 10⁻⁴
        """
        return self.calculate_total_system_failure_prob() <= self.MAX_SYSTEM_FAILURE_PROB
