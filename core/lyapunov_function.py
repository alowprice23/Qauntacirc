# core/lyapunov_function.py

from core.types import QCState

class LyapunovFunction:
    def __init__(self, kappa: float, xi: float):
        if kappa <= 0 or xi <= 0:
            raise ValueError("Weights kappa and xi must be positive.")
        self.kappa = kappa
        self.xi = xi

    def compute(self, state: QCState) -> float:
        return state.energy + self.kappa * state.failing_tests + self.xi * state.open_obligations

    def get_components(self, state: QCState) -> dict:
        return {
            "energy": state.energy,
            "test_penalty": self.kappa * state.failing_tests,
            "obligation_penalty": self.xi * state.open_obligations,
        }
