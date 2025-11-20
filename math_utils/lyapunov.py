import numpy as np

class LyapunovFunction:
    """
    Represents a Lyapunov function for stability analysis of a dynamical system.

    A function V(x) is a Lyapunov function for a system x_dot = f(x) if
    V(x) > 0 for x != 0, V(0) = 0, and dV/dt <= 0 along the system's trajectories.
    """
    def __init__(self, function_type='quadratic', P=None):
        """
        Initializes the Lyapunov function.

        Args:
            function_type (str): Type of Lyapunov function ('quadratic' or 'general').
            P (np.ndarray, optional): For a quadratic Lyapunov function V(x) = x.T * P * x,
                                     P is a positive definite matrix. Defaults to None.
        """
        self.function_type = function_type
        if function_type == 'quadratic':
            if P is None:
                raise ValueError("Matrix P must be provided for a quadratic Lyapunov function.")
            self.P = P
            if not self._is_positive_definite(P):
                raise ValueError("Matrix P for a quadratic Lyapunov function must be positive definite.")

    def _is_positive_definite(self, A):
        """Checks if a matrix is positive definite."""
        return np.all(np.linalg.eigvals(A) > 0)

    def evaluate(self, x):
        """Evaluates the Lyapunov function at a given state x."""
        if self.function_type == 'quadratic':
            return x.T @ self.P @ x
        else:
            # For a general Lyapunov function, this method should be overridden
            raise NotImplementedError("evaluate() must be implemented for a general Lyapunov function.")

    def derivative(self, x, x_dot):
        """
        Evaluates the time derivative of the Lyapunov function along the system's trajectory.

        For V(x) = x.T * P * x, dV/dt = x_dot.T * P * x + x.T * P * x_dot.
        """
        if self.function_type == 'quadratic':
            return x_dot.T @ self.P @ x + x.T @ self.P @ x_dot
        else:
            raise NotImplementedError("derivative() must be implemented for a general Lyapunov function.")

class StabilityAnalyzer:
    """
    Analyzes the stability of a system using Lyapunov's direct method.
    """
    def __init__(self, lyapunov_function: LyapunovFunction, system_dynamics):
        """
        Initializes the stability analyzer.

        Args:
            lyapunov_function (LyapunovFunction): The Lyapunov function for the system.
            system_dynamics (callable): A function f(x) that returns x_dot, the time
                                        derivative of the system's state.
        """
        self.lyapunov_function = lyapunov_function
        self.system_dynamics = system_dynamics

    def check_stability(self, x):
        """
        Checks the stability of the system at a given state x.

        Returns:
            str: 'stable', 'asymptotically stable', or 'unstable'.
        """
        v_x = self.lyapunov_function.evaluate(x)
        if v_x <= 0 and not np.all(x == 0):
            return 'unstable' # V(x) is not positive definite

        x_dot = self.system_dynamics(x)
        v_dot = self.lyapunov_function.derivative(x, x_dot)

        if v_dot > 0:
            return 'unstable'
        elif v_dot < 0:
            return 'asymptotically stable'
        else: # v_dot == 0
            return 'stable'

    def estimate_stability_rate(self, x):
        """
        Estimates the exponential stability rate if the system is exponentially stable.

        Requires V_dot(x) <= -alpha * V(x) for some alpha > 0.
        """
        v_x = self.lyapunov_function.evaluate(x)
        if v_x == 0:
            return np.inf # Rate is infinite at the origin

        x_dot = self.system_dynamics(x)
        v_dot = self.lyapunov_function.derivative(x, x_dot)

        if v_dot >= 0:
            return 0 # Not exponentially stable

        # alpha = -V_dot(x) / V(x)
        return -v_dot / v_x

    def validate_trajectory(self, trajectory):
        """
        Validates that the Lyapunov function is non-increasing along a given trajectory.

        Args:
            trajectory (list of np.ndarray): A list of states over time.

        Returns:
            bool: True if the trajectory is stable, False otherwise.
        """
        v_values = [self.lyapunov_function.evaluate(x) for x in trajectory]
        for i in range(len(v_values) - 1):
            if v_values[i+1] > v_values[i]:
                return False
        return True
<<<<<<< HEAD
<<<<<<< HEAD


def is_lyapunov_stable(state_vector: np.ndarray) -> bool:
    """
    A simplified stability check using a default Lyapunov analyzer.
    Assumes a simple quadratic Lyapunov function and linear dynamics.
    """
    if not isinstance(state_vector, np.ndarray):
        state_vector = np.array(state_vector)

    # Define a default positive definite matrix for V(x) = x.T * P * x
    P = np.eye(len(state_vector))
    lyapunov_func = LyapunovFunction(P=P)

    # Define simple linear system dynamics, x_dot = -x, which is stable
    def system_dynamics(x):
        return -x

    analyzer = StabilityAnalyzer(lyapunov_func, system_dynamics)
    stability = analyzer.check_stability(state_vector)

    return stability in ['stable', 'asymptotically stable']

def estimate_lyapunov_exponent(trajectory: np.ndarray, dt: float = 1.0) -> float:
    """
    Estimates the largest Lyapunov exponent from a time series.

    This method uses the average logarithmic growth rate of the trajectory values
    as a heuristic for the Lyapunov exponent. A positive exponent suggests chaos
    (divergence), while a negative one suggests stability (convergence).

    Args:
        trajectory: A 1D numpy array representing the time series.
        dt: The time step between trajectory points.

    Returns:
        The estimated Lyapunov exponent.
    """
    if len(trajectory) < 2:
        return 0.0

    # Ensure trajectory has no zeros to avoid log(0)
    # Add a small epsilon to zeros, or filter them out.
    # For this heuristic, we assume non-zero potentials.
    # A zero potential would imply reaching the target state.

    # Create a copy to avoid modifying the original array
    traj_no_zeros = np.copy(trajectory.astype(float))
    traj_no_zeros[traj_no_zeros == 0] = 1e-9

    # Calculate the average logarithmic rate of change
    log_ratios = np.log(np.abs(traj_no_zeros[1:] / traj_no_zeros[:-1]))

    # Filter out any non-finite values that might arise
    finite_ratios = log_ratios[np.isfinite(log_ratios)]
    if len(finite_ratios) == 0:
        return 0.0

    return np.mean(finite_ratios) / dt
=======
>>>>>>> remotes/origin/feat/core-infrastructure
=======
>>>>>>> remotes/origin/feat/core-infrastructure
