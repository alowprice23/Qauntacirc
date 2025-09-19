import numpy as np
from . import lipschitz as lip
from . import contractive_maps as cmaps
from . import lyapunov as lyap
from core.types import SystemState, CoverageReport, PropertySpecification, LogicType

class ConvergenceCertificate:
    """
    Generates a certificate of convergence for an optimization algorithm.

    This class collects evidence during an optimization run and provides a summary
    that can be used to certify the convergence with mathematical reasoning.
    """
    def __init__(self, algorithm_name, params):
        self.algorithm_name = algorithm_name
        self.params = params
        self.log = []
        self.proof = "No proof generated yet."

    def add_log(self, iteration, state, value, grad_norm=None):
        """Adds a log entry for the current state of the optimization."""
        self.log.append({
            'iteration': iteration,
            'state': np.copy(state),
            'value': value,
            'grad_norm': grad_norm
        })

    def generate_proof(self, properties):
        """
        Generates a human-readable proof of convergence based on the collected evidence.

        Args:
            properties (dict): A dictionary of verified properties of the energy function
                               and algorithm (e.g., {'is_convex': True, 'pl_constant': 0.1}).
        """
        proof_lines = [f"Convergence Certificate for {self.algorithm_name}:"]
        proof_lines.append("-" * 40)

        if properties.get('is_convex'):
            proof_lines.append("- The energy function has been verified as convex.")
        if properties.get('pl_constant'):
            proof_lines.append(f"- The function satisfies the PL inequality with mu={properties['pl_constant']:.4f}.")
        if properties.get('is_contraction'):
            proof_lines.append(f"- The iterative map is a contraction with k={properties['contraction_factor']:.4f}.")

        final_grad_norm = self.log[-1]['grad_norm']
        if final_grad_norm is not None and final_grad_norm < 1e-5:
            proof_lines.append(f"- Final gradient norm {final_grad_norm:.2e} is below the threshold.")

        self.proof = "\n".join(proof_lines)
        return self.proof

def verify_convexity(func, space, samples=100):
    """
    Empirically verifies the convexity of a function over a given space.

    Checks if f(alpha*x + (1-alpha)*y) <= alpha*f(x) + (1-alpha)*f(y).
    """
    lower_bound, upper_bound, dim = space
    for _ in range(samples):
        x = np.random.uniform(lower_bound, upper_bound, dim)
        y = np.random.uniform(lower_bound, upper_bound, dim)
        alpha = np.random.rand()

        mid_point_val = func(alpha * x + (1 - alpha) * y)
        interp_val = alpha * func(x) + (1 - alpha) * func(y)

        if mid_point_val > interp_val + 1e-9: # Add tolerance for numerical errors
            return False, "Function is not convex."

    return True, "Function appears to be convex."

def verify_smoothness(grad_func, space, samples=100):
    """
    Empirically verifies the smoothness (Lipschitz continuity of the gradient) of a function.

    Checks if ||grad(f(x)) - grad(f(y))|| <= L * ||x - y|| for some L.
    Returns the estimated Lipschitz constant L.
    """
    lower_bound, upper_bound, dim = space
    max_l = 0
    for _ in range(samples):
        x = np.random.uniform(lower_bound, upper_bound, dim)
        y = np.random.uniform(lower_bound, upper_bound, dim)

        dist_xy = np.linalg.norm(x - y)
        if dist_xy < 1e-9:
            continue

        grad_dist = np.linalg.norm(grad_func(x) - grad_func(y))
        l_val = grad_dist / dist_xy

        if l_val > max_l:
            max_l = l_val

    return max_l, "Estimated Lipschitz constant for the gradient."


def compute_verification_coverage(system_state: SystemState) -> CoverageReport:
    """
    Compute verification coverage across all logics

    Coverage = (Verified Properties) / (Total Properties) by category
    """

    total_properties = classify_system_properties(system_state)
    verified_properties = {category: [] for category in total_properties.keys()}

    # Analyze verification results by property category
    for result in system_state.verification_results:
        if result.success and result.logic_results:
            property_category = classify_property(result.property_spec)
            verified_properties[property_category].append(result.property_spec)

    # Compute coverage percentages
    coverage_by_category = {}
    for category, props in total_properties.items():
        total = len(props)
        verified = len(verified_properties.get(category, []))
        coverage_by_category[category] = (verified / total * 100) if total > 0 else 100.0

    # Compute overall formal coverage
    total_all = sum(len(props) for props in total_properties.values())
    verified_all = sum(len(props) for props in verified_properties.values())
    overall_coverage = (verified_all / total_all * 100) if total_all > 0 else 100.0

    return CoverageReport(
        overall_coverage=overall_coverage,
        by_category=coverage_by_category,
        by_logic=compute_coverage_by_logic(system_state.verification_results),
        uncovered_properties=compute_uncovered_properties(total_properties, verified_properties)
    )

def classify_system_properties(system_state: SystemState) -> dict:
    """Classify all properties required by the system state."""
    # Mock implementation: In a real system, this would inspect the code,
    # requirements, etc., to determine all properties that need verification.
    return {
        "functional": [PropertySpecification(id="p1", description="desc1", category="functional")],
        "performance": [PropertySpecification(id="p2", description="desc2", category="performance")]
    }

def classify_property(property_spec: PropertySpecification) -> str:
    """Classify a single property spec into a category."""
    # Mock implementation
    return property_spec.category

def compute_coverage_by_logic(verification_results: list) -> dict:
    """Compute coverage percentage for each logic used."""
    # Mock implementation
    logic_coverage = {logic.value: 0 for logic in LogicType}
    if not verification_results:
        return logic_coverage

    logic_counts = {logic.value: 0 for logic in LogicType}
    logic_success = {logic.value: 0 for logic in LogicType}

    for result in verification_results:
        if result.logic_results:
            for logic, res in result.logic_results.items():
                logic_counts[logic.value] += 1
                if res.success:
                    logic_success[logic.value] += 1

    for logic_str in logic_coverage.keys():
        if logic_counts[logic_str] > 0:
            logic_coverage[logic_str] = (logic_success[logic_str] / logic_counts[logic_str]) * 100

    return logic_coverage

def compute_uncovered_properties(total_properties: dict, verified_properties: dict) -> list:
    """Determine which properties from the total set have not been verified."""
    uncovered = []
    verified_ids = {prop.id for cat_props in verified_properties.values() for prop in cat_props}

    for category, props in total_properties.items():
        for prop in props:
            if prop.id not in verified_ids:
                uncovered.append(prop)
    return uncovered
