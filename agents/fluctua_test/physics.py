import numpy as np
from scipy.integrate import simps

class GreenKubo:
    """
    Implements the Green-Kubo relation to calculate viscosity.
    """
    def __init__(self, V, kT):
        self.V = V
        self.kT = kT

    def calculate_viscosity(self, stress_tensor_history, time_points):
        """
        Calculates viscosity using the Green-Kubo relation.

        η = V/kT ∫₀^∞ ⟨σ(0)σ(t)⟩dt

        Args:
            stress_tensor_history (list): A list of stress tensors over time.
            time_points (list): A list of time points.

        Returns:
            float: The calculated viscosity.
        """
        if len(stress_tensor_history) != len(time_points):
            raise ValueError("stress_tensor_history and time_points must have the same length.")

        autocorrelation = self._calculate_autocorrelation(stress_tensor_history)
        integral = simps(autocorrelation, time_points)
        viscosity = (self.V / self.kT) * integral
        return viscosity

    def _calculate_autocorrelation(self, stress_tensor_history):
        """
        Calculates the autocorrelation of the stress tensor.
        """
        n = len(stress_tensor_history)
        autocorrelation = np.zeros(n)
        for t in range(n):
            for t0 in range(n - t):
                autocorrelation[t] += np.dot(stress_tensor_history[t0], stress_tensor_history[t0 + t])
            autocorrelation[t] /= (n - t)
        return autocorrelation
