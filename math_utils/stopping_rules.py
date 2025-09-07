import numpy as np

class OptimizationStopper:
    """
    A class to manage stopping criteria for optimization algorithms.
    """
    def __init__(self, max_iter=1000, grad_norm_tol=1e-5, energy_tol=1e-6, stagnation_tol=1e-7, stagnation_window=10):
        self.max_iter = max_iter
        self.grad_norm_tol = grad_norm_tol
        self.energy_tol = energy_tol
        self.stagnation_tol = stagnation_tol
        self.stagnation_window = stagnation_window
        self.history = {'energy': [], 'grad_norm': []}
        self.iter = 0

    def reset(self):
        """Resets the stopper's state for a new optimization run."""
        self.history = {'energy': [], 'grad_norm': []}
        self.iter = 0

    def should_stop(self, current_iter, grad_norm, energy_value):
        """
        Checks if any of the stopping criteria are met.

        Args:
            current_iter (int): The current iteration number.
            grad_norm (float): The norm of the gradient at the current point.
            energy_value (float): The value of the objective function (energy).

        Returns:
            bool: True if the optimization should stop, False otherwise.
            str: The reason for stopping.
        """
        self.iter = current_iter
        self.history['grad_norm'].append(grad_norm)
        self.history['energy'].append(energy_value)

        # 1. Maximum iteration safeguard
        if self.iter >= self.max_iter:
            return True, "Maximum iterations reached."

        # 2. Gradient norm-based stopping
        if grad_norm < self.grad_norm_tol:
            return True, f"Gradient norm below tolerance ({self.grad_norm_tol})."

        # 3. Energy stabilization detection
        if len(self.history['energy']) > 1:
            energy_change = np.abs(self.history['energy'][-1] - self.history['energy'][-2])
            if energy_change < self.energy_tol:
                # Add a confidence check using a window
                if len(self.history['energy']) > self.stagnation_window:
                    windowed_change = np.std(self.history['energy'][-self.stagnation_window:])
                    if windowed_change < self.energy_tol:
                        return True, f"Energy stabilized within tolerance ({self.energy_tol})."

        # 4. Stagnation detection
        if len(self.history['energy']) > self.stagnation_window:
            stagnation_change = np.abs(self.history['energy'][-1] - self.history['energy'][-self.stagnation_window])
            if stagnation_change < self.stagnation_tol:
                return True, f"Stagnation detected over the last {self.stagnation_window} iterations."

        return False, "Not stopped."

    def get_stopping_reason(self, grad_norm, energy_value):
        """
        Provides the reason for the last stopping decision without advancing the state.
        This is useful for logging without affecting the stopping logic.
        """
        stop, reason = self.should_stop(self.iter, grad_norm, energy_value)
        # Rewind state changes from the check
        self.history['grad_norm'].pop()
        self.history['energy'].pop()
        return reason
