import math
import numpy as np
from typing import Dict
from core.types import WorkloadDistribution

class BoseEinsteinStatistics:
    def __init__(self, k_B=8.617333e-5):
        self.k_B = k_B

    def extract_task_energy_levels(self, workload: WorkloadDistribution) -> Dict[str, float]:
        """Extracts task energy levels from the workload, using complexity as a proxy for energy."""
        return {
            task_type: data.get('complexity', 1.0) * 1e-5
            for task_type, data in workload.tasks.items()
        }

    def compute_chemical_potential(self, total_resources: float, energy_levels: Dict[str, float], T: float) -> float:
        """Solves for the chemical potential μ that satisfies the total resource constraint."""
        if not energy_levels: return 0.0
        min_energy = min(energy_levels.values())

        def f(mu):
            if mu >= min_energy: return float('inf')
            kT = self.k_B * T
            return sum(1.0 / (math.exp((epsilon - mu) / kT) - 1.0) for epsilon in energy_levels.values()) - total_resources

        low = min_energy - 5 * abs(min_energy) if min_energy != 0 else -5.0
        high = min_energy - 1e-9

        try:
            f_low = f(low)
            f_high = f(high)
            if f_low * f_high >= 0:
                return high if f_high < 0 else low
        except (ValueError, OverflowError):
            return min_energy - 1.0 # Fallback

        for _ in range(100):
            mid = (low + high) / 2
            if mid == low or mid == high: break
            f_mid = f(mid)
            if f_mid < 0: high = mid
            else: low = mid

        return (low + high) / 2
