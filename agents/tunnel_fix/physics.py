import numpy as np

class QuantumTunneling:
    def __init__(self, transmission_coeff=1.0):
        self.transmission_coeff = transmission_coeff

    def compute_tunneling_probability(self,
                                     barrier_height: float,
                                     barrier_width: float,
                                     temperature: float) -> float:
        """
        Compute tunneling probability using quantum mechanics formula
        T = A * exp(-2κd) where κ = √(2m(V-E))/ℏ
        """
        if temperature <= 0:
            return 0.0

        kappa = np.sqrt(2 * barrier_height / temperature)
        distance = barrier_width

        tunneling_prob = self.transmission_coeff * np.exp(-2 * kappa * distance)

        return min(1.0, tunneling_prob)
