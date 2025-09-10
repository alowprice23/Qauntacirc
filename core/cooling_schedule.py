# core/cooling_schedule.py

import math

class LogarithmicCooling:
    def __init__(self, c: float):
        if c <= 0:
            raise ValueError("Temperature constant c must be positive.")
        self.c = c

    def temperature(self, k: int) -> float:
        return self.c / math.log(k + 2)

class GeometricCooling:
    def __init__(self, alpha: float, initial_temperature: float):
        if not (0 < alpha < 1):
            raise ValueError("Cooling rate alpha must be in (0, 1).")
        if initial_temperature <= 0:
            raise ValueError("Initial temperature must be positive.")
        self.alpha = alpha
        self.initial_temperature = initial_temperature

    def temperature(self, k: int) -> float:
        return self.initial_temperature * (self.alpha ** k)
