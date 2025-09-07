import numpy as np
from . import lipschitz as lip
from . import contractive_maps as cmaps
from . import lyapunov as lyap

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
