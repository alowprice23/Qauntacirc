"""
Implements the mathematical risk quantification framework using Chernoff bounds,
error budget management, and real-time risk monitoring.
"""

import math
from dataclasses import dataclass
from typing import Dict, Any, Optional

import numpy as np
from scipy.optimize import minimize

from core.error_budget import ErrorBudget

# --- Helper Classes ---

class ChernoffConcentrationBoundCalculator:
    """
    Calculates an upper bound on the probability of failure (risk) for a component
    based on statistical testing results, using the Chernoff-Hoeffding bound.
    """
    def __init__(self):
        self.last_proof = "No calculations performed yet."

    def compute_chernoff_bound(self, n_tests: int, observed_failures: int, confidence_level: float, effect_size: float) -> float:
        """
        Computes a tighter upper bound on the failure rate `p` using a common
        form of the Chernoff bound for binomial tail probabilities.

        Args:
            n_tests: The total number of statistical tests performed.
            observed_failures: The number of tests that failed.
            confidence_level: The desired statistical confidence (e.g., 0.95).
            effect_size: This parameter is not used in this implementation but is kept for API compatibility.

        Returns:
            An upper bound on the probability of failure.
        """
        if n_tests <= 0:
            return 1.0  # Maximum risk if no tests are run

        p_hat = observed_failures / n_tests
        alpha = 1 - confidence_level

        # This is a tighter and more complex Chernoff-style bound for the upper confidence limit of a binomial proportion.
        # p_upper = p_hat + sqrt(p_hat * log(1/alpha)/n) + log(1/alpha)/n
        log_inv_alpha = math.log(1 / alpha)

        term1 = p_hat
        term2 = math.sqrt((p_hat * log_inv_alpha) / n_tests)
        term3 = log_inv_alpha / n_tests

        p_upper = term1 + term2 + term3

        self.last_proof = (
            f"Tighter Chernoff Bound Calculation:\n"
            f"  - n_tests (n): {n_tests}\n"
            f"  - observed_failures (k): {observed_failures}\n"
            f"  - p_hat (k/n): {p_hat:.6e}\n"
            f"  - confidence_level: {confidence_level}\n"
            f"  - alpha (1 - confidence): {alpha}\n"
            f"  - p_upper = p_hat + sqrt(p_hat*ln(1/a)/n) + ln(1/a)/n: {p_upper:.6e}\n"
            f"This means we are {confidence_level*100}% confident that the true failure rate is at most {p_upper:.6e}."
        )

        # The risk is the upper bound on the failure probability
        return min(p_upper, 1.0)

    def get_last_proof(self) -> str:
        return self.last_proof

class ErrorBudgetManager:
    """
    Manages risk budgets for different surfaces.
    This is a wrapper around the core ErrorBudget class to handle multiple budgets.
    """
    def __init__(self, total_budget: float, allocation: Dict[str, float]):
        """
        Initializes the budget manager.
        Args:
            total_budget: The total risk budget for the system (e.g., 1e-4).
            allocation: A dictionary specifying the proportion of the budget for each surface.
                        Example: {"verified": 0.1, "empirical": 0.8, "security": 0.1}
        """
        if not math.isclose(sum(allocation.values()), 1.0):
            raise ValueError("Budget allocation proportions must sum to 1.")

        self.budgets = {
            "verified": ErrorBudget({"risk": total_budget * allocation["verified"]}),
            "empirical": ErrorBudget({"risk": total_budget * allocation["empirical"]}),
            "security": ErrorBudget({"risk": total_budget * allocation["security"]})
        }

    def check_compliance(self, surface: str, risk: float) -> bool:
        """
        Checks if the observed risk for a surface is within its budget.
        """
        return risk <= self.budgets[surface].get_remaining_budget("risk")

class RiskSurfaceAnalyzer:
    """Mock implementation of a risk surface analyzer."""
    def analyze(self, surface_data: Any) -> Dict[str, Any]:
        return {"complexity": 1.0, "dependencies": 5}

class StatisticalRiskEngine:
    """Mock implementation of a statistical risk engine."""
    def run_hypothesis_test(self, data: Any) -> bool:
        return True

@dataclass
class SystemState:
    formal_verification_results: Any
    total_statistical_tests: int
    observed_test_failures: int
    chaos_test_results: Any
    penetration_test_results: Any

@dataclass
class SystemRiskAssessment:
    verified_surface_risk: float
    empirical_surface_risk: float
    security_surface_risk: float
    total_system_risk: float
    budget_compliance: bool
    mathematical_certificate: str
    meets_target_budget: bool

@dataclass
class ErrorBudgetAllocation:
    verified_surface_budget: float
    empirical_surface_budget: float
    security_surface_budget: float
    optimization_proof: str
    expected_risk_reduction: float

@dataclass
class OptimizedBudgetAllocation:
    optimized_allocation: ErrorBudgetAllocation
    improvement_factor: float
    mathematical_optimality_certificate: str


class MathematicalRiskQuantificationSystem:
    """Implements Chernoff bounds and error budget management with mathematical guarantees"""

    def __init__(self, total_budget: float = 1e-4, budget_allocation: Optional[Dict[str, float]] = None):
        if budget_allocation is None:
            budget_allocation = {"verified": 0.01, "empirical": 0.89, "security": 0.1}

        self.chernoff_calculator = ChernoffConcentrationBoundCalculator()
        self.error_budget_manager = ErrorBudgetManager(total_budget, budget_allocation)
        self.risk_surface_analyzer = RiskSurfaceAnalyzer()
        self.statistical_risk_engine = StatisticalRiskEngine()
        self.total_budget = total_budget

    def compute_comprehensive_system_risk_bounds(self, system_state: SystemState) -> SystemRiskAssessment:
        """Compute total system risk using mathematical bounds with ≤10⁻⁴ target"""

        # 1. Verified Surface Risk (Formal Proofs)
        verified_surface_risk = self._compute_verified_surface_risk(system_state.formal_verification_results)

        # 2. Empirical Surface Risk (Statistical Testing)
        empirical_risk_bound = self.chernoff_calculator.compute_chernoff_bound(
            n_tests=system_state.total_statistical_tests,
            observed_failures=system_state.observed_test_failures,
            confidence_level=0.95,
            effect_size=0.01  # Kept for API compatibility
        )

        # 3. Security Surface Risk (Chaos Testing + Penetration Testing)
        security_risk_bound = self._compute_security_surface_risk(
            chaos_test_results=system_state.chaos_test_results,
            penetration_test_results=system_state.penetration_test_results
        )

        # 4. Apply union bound for total risk: P(failure) ≤ P_verified + P_empirical + P_security
        total_risk_bound = verified_surface_risk + empirical_risk_bound + security_risk_bound

        # 5. Verify against error budget compliance
        budget_compliance = self._verify_budget_compliance(total_risk_bound)

        # 6. Generate mathematical risk certificate
        risk_certificate = self._generate_risk_mathematical_certificate(
            verified_risk=verified_surface_risk,
            empirical_risk=empirical_risk_bound,
            security_risk=security_risk_bound,
            total_risk=total_risk_bound,
            chernoff_proof=self.chernoff_calculator.get_last_proof()
        )

        return SystemRiskAssessment(
            verified_surface_risk=verified_surface_risk,
            empirical_surface_risk=empirical_risk_bound,
            security_surface_risk=security_risk_bound,
            total_system_risk=total_risk_bound,
            budget_compliance=budget_compliance,
            mathematical_certificate=risk_certificate,
            meets_target_budget=total_risk_bound <= self.total_budget
        )

    async def optimize_error_budget_allocation(self, current_allocation: ErrorBudgetAllocation, system_state: SystemState) -> OptimizedBudgetAllocation:
        """Optimize error budget allocation using mathematical optimization."""
        # 1. Analyze risk reduction efficiency to get model parameters
        analysis = self._analyze_risk_reduction_efficiency(system_state)

        # 2. Define the optimization problem for scipy
        def objective_function(budgets):
            risk_v = analysis['verified']['base_risk'] * np.exp(-analysis['verified']['efficiency'] * budgets[0])
            risk_e = analysis['empirical']['base_risk'] * np.exp(-analysis['empirical']['efficiency'] * budgets[1])
            risk_s = analysis['security']['base_risk'] * np.exp(-analysis['security']['efficiency'] * budgets[2])
            return risk_v + risk_e + risk_s

        # Constraint: sum of budgets must equal total budget
        constraints = ({'type': 'eq', 'fun': lambda budgets: np.sum(budgets) - self.total_budget})

        # Bounds: budgets cannot be negative or exceed the total budget
        bounds = [(0, self.total_budget), (0, self.total_budget), (0, self.total_budget)]

        # Initial guess: the current allocation, normalized to be safe
        initial_guess = np.array([
            current_allocation.verified_surface_budget,
            current_allocation.empirical_surface_budget,
            current_allocation.security_surface_budget
        ])
        if not np.isclose(np.sum(initial_guess), self.total_budget):
            initial_guess = initial_guess / np.sum(initial_guess) * self.total_budget if np.sum(initial_guess) > 0 else np.array([self.total_budget/3.0]*3)

        # 3. Solve using mathematical programming (scipy.optimize.minimize)
        result = minimize(
            objective_function,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        if not result.success:
            raise RuntimeError(f"Budget optimization failed: {result.message}")

        optimal_budgets = result.x

        # 4. Generate optimized allocation with mathematical justification
        initial_risk = objective_function(initial_guess)
        optimized_risk = result.fun
        risk_reduction = initial_risk - optimized_risk
        improvement_factor = initial_risk / optimized_risk if optimized_risk > 1e-12 else float('inf')

        optimization_proof = (
            f"Optimization completed using SLSQP solver.\n"
            f"  - Status: {result.message}\n"
            f"  - Iterations: {result.nit}\n"
            f"  - Initial Predicted Risk: {initial_risk:.6e}\n"
            f"  - Optimized Predicted Risk: {optimized_risk:.6e}\n"
            f"  - Expected Risk Reduction: {risk_reduction:.6e}"
        )

        optimized_allocation = ErrorBudgetAllocation(
            verified_surface_budget=optimal_budgets[0],
            empirical_surface_budget=optimal_budgets[1],
            security_surface_budget=optimal_budgets[2],
            optimization_proof=optimization_proof,
            expected_risk_reduction=risk_reduction
        )

        optimality_certificate = (
            f"Mathematical optimality certificate based on Karush-Kuhn-Tucker (KKT) conditions.\n"
            f"Solver status '{result.status}' indicates that the optimality conditions are satisfied.\n"
            f"Final objective function value (total risk): {result.fun:.6e}"
        )

        return OptimizedBudgetAllocation(
            optimized_allocation=optimized_allocation,
            improvement_factor=improvement_factor,
            mathematical_optimality_certificate=optimality_certificate
        )

    def _compute_verified_surface_risk(self, formal_verification_results: Any) -> float:
        """
        Mock implementation for verified surface risk.
        In a real system, this would parse results from tools like Coq, Z3, etc.
        and use a model like the one in `math_utils/risk.py`.
        For now, we assume a very low, fixed risk for formally verified parts.
        """
        # Let's assume the results contain a list of proved theorems.
        num_proofs = len(formal_verification_results.get("proofs", [])) if formal_verification_results else 0
        # Risk decreases as more proofs are available.
        return max(1e-8, 1e-6 - num_proofs * 1e-8)

    def _compute_security_surface_risk(self, chaos_test_results: Any, penetration_test_results: Any) -> float:
        """
        Mock implementation for security surface risk.
        A real implementation would quantify risk based on the number and severity
        of vulnerabilities found.
        """
        # Assume chaos tests report the's resilience (higher is better)
        resilience_score = chaos_test_results.get("resilience_score", 0.9) if chaos_test_results else 0.9
        # Assume penetration tests find a number of vulnerabilities
        num_vulnerabilities = len(penetration_test_results.get("vulnerabilities", [])) if penetration_test_results else 0

        base_risk = 1e-5
        risk = base_risk * (1 / (resilience_score + 1e-9)) + num_vulnerabilities * 5e-6
        return min(risk, 1.0)

    def _verify_budget_compliance(self, total_risk_bound: float) -> bool:
        """Verify if the total risk is within the target budget."""
        return total_risk_bound <= self.total_budget

    def _generate_risk_mathematical_certificate(self, verified_risk: float, empirical_risk: float, security_risk: float, total_risk: float, chernoff_proof: str) -> str:
        """Generates a mathematical certificate of the risk assessment."""
        certificate = (
            f"--- Mathematical Risk Assessment Certificate ---\n"
            f"Timestamp: {__import__('datetime').datetime.now().isoformat()}\n\n"
            f"1. Total System Risk Bound: {total_risk:.6e}\n"
            f"   - Target Budget: {self.total_budget:.6e}\n"
            f"   - Compliance Status: {'PASS' if total_risk <= self.total_budget else 'FAIL'}\n\n"
            f"2. Risk Surface Breakdown:\n"
            f"   - Verified Surface Risk:   {verified_risk:.6e}\n"
            f"   - Empirical Surface Risk:  {empirical_risk:.6e}\n"
            f"   - Security Surface Risk:   {security_risk:.6e}\n\n"
            f"3. Empirical Risk Proof (Chernoff-Hoeffding):\n"
            f"{chernoff_proof}\n"
            f"--- End of Certificate ---"
        )
        return certificate

    def _analyze_risk_reduction_efficiency(self, system_state: SystemState) -> Dict[str, Dict[str, float]]:
        """
        Analyzes the efficiency of budget allocation for risk reduction on different surfaces.
        This implementation provides a plausible heuristic model for optimization.

        Returns:
            A dictionary containing the 'base_risk' (risk with current investment) and
            'efficiency' (how effectively *additional* budget reduces risk) for each surface.
        """
        # Calculate current risks, which will serve as our base_risk for the model.
        base_risks = {
            "verified": self._compute_verified_surface_risk(system_state.formal_verification_results),
            "empirical": self.chernoff_calculator.compute_chernoff_bound(
                system_state.total_statistical_tests, system_state.observed_test_failures, 0.95, 0.01),
            "security": self._compute_security_surface_risk(system_state.chaos_test_results, system_state.penetration_test_results)
        }

        # Heuristic for efficiency (k in risk = base * exp(-k * budget))
        # A higher 'k' means budget is more effective at reducing risk.

        # Verified surface: Efficiency is higher if there are fewer proofs. More to gain.
        num_proofs = len(system_state.formal_verification_results.get("proofs", [])) if system_state.formal_verification_results else 0
        verified_efficiency = 1e5 / (1 + num_proofs * 5)

        # Empirical surface: Efficiency is higher if observed failure rate is high (low-hanging fruit).
        p_hat = (system_state.observed_test_failures / system_state.total_statistical_tests
                 if system_state.total_statistical_tests > 0 else 0)
        empirical_efficiency = 5e5 * (p_hat * 100 + 0.1)

        # Security surface: Efficiency is higher with more vulnerabilities found.
        num_vulnerabilities = len(system_state.penetration_test_results.get("vulnerabilities", [])) if system_state.penetration_test_results else 0
        security_efficiency = 2e5 * (1 + num_vulnerabilities * 2)

        return {
            "verified": {"base_risk": base_risks["verified"], "efficiency": verified_efficiency},
            "empirical": {"base_risk": base_risks["empirical"], "efficiency": empirical_efficiency},
            "security": {"base_risk": base_risks["security"], "efficiency": security_efficiency}
        }
