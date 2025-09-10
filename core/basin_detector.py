# core/basin_detector.py

import numpy as np

class BasinDetector:
    def __init__(self, window_size: int = 50, variance_threshold: float = 0.01, gradient_threshold: float = 1e-3):
        self.window_size = window_size
        self.variance_threshold = variance_threshold
        self.gradient_threshold = gradient_threshold
        self.energy_history = []
        self.gradient_history = []

    def update(self, iteration: int, energy: float, gradient_norm: float):
        self.energy_history.append(energy)
        self.gradient_history.append(gradient_norm)

    def in_basin(self) -> bool:
        if len(self.energy_history) < self.window_size:
            return False

        recent_energies = self.energy_history[-self.window_size:]
        recent_gradients = self.gradient_history[-self.window_size:]

        energy_variance = np.var(recent_energies)
        avg_gradient_norm = np.mean(recent_gradients)

        return energy_variance < self.variance_threshold and avg_gradient_norm < self.gradient_threshold

    def get_statistics(self) -> dict:
        if len(self.energy_history) < self.window_size:
            return {'energy_variance': np.inf, 'gradient_norm': np.inf}

        recent_energies = self.energy_history[-self.window_size:]
        recent_gradients = self.gradient_history[-self.window_size:]
        return {
            'energy_variance': np.var(recent_energies),
            'gradient_norm': np.mean(recent_gradients)
        }
