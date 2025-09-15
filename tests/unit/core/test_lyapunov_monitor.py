import pytest
import numpy as np
import time

from core.types import SystemState, LyapunovValue, BoundedExcursion, TestResult, ProofObligation
from core.lyapunov_monitor import (
    compute_lyapunov_function,
    detect_bounded_excursions,
    verify_martingale_convergence
)

class TestLyapunovFunctions:
    def test_compute_lyapunov_function(self):
        """
        Tests the correct computation of the Lyapunov function.
        """
        state = SystemState(
            test_results=[TestResult(name="t1", passed=False), TestResult(name="t2", passed=True)],
            proof_obligations=[ProofObligation(id="p1", status="open"), ProofObligation(id="p2", status="closed")],
            approximated_energy=10.0
        )

        # With kappa=100, xi=50
        # Expected: 10 (energy) + 100*1 (failing test) + 50*1 (open obligation) = 160
        lyapunov_value = compute_lyapunov_function(state, kappa=100.0, xi=50.0)

        assert isinstance(lyapunov_value, LyapunovValue)
        assert lyapunov_value.total == 160.0
        assert lyapunov_value.energy_component == 10.0
        assert lyapunov_value.test_component == 100.0
        assert lyapunov_value.obligation_component == 50.0
        assert isinstance(lyapunov_value.timestamp, float)

    def test_detect_bounded_excursions_no_excursion(self):
        """
        Tests that no excursion is detected in a steadily decreasing trajectory.
        """
        phi_history = [LyapunovValue(total=100 - i, energy_component=0, test_component=0, obligation_component=0, timestamp=time.time()) for i in range(100)]
        excursions = detect_bounded_excursions(phi_history, window_size=20)
        assert len(excursions) == 0

    def test_detect_bounded_excursions_with_valid_excursion(self):
        """
        Tests detection of a valid, bounded excursion.
        """
        # Create a base decreasing trajectory
        phi_vals = [100 - i*0.2 for i in range(150)]
        # Inject a more pronounced excursion
        excursion_start = 60
        excursion_peak = 75
        for i in range(excursion_start, excursion_peak): # Increase for 15 steps
            phi_vals[i] += (i - excursion_start) * 0.5
        # Recovery phase
        for i in range(excursion_peak, excursion_peak + 20):
             phi_vals[i] = phi_vals[excursion_peak-1] - (i - (excursion_peak-1)) * 0.4


        phi_history = [LyapunovValue(total=v, energy_component=0, test_component=0, obligation_component=0, timestamp=time.time()) for v in phi_vals]

        excursions = detect_bounded_excursions(phi_history, window_size=30, excursion_tolerance=10.0)

        assert len(excursions) > 0
        assert isinstance(excursions[0], BoundedExcursion)
        assert excursions[0].magnitude < 10.0

    def test_detect_bounded_excursions_unbounded(self):
        """
        Tests that an excursion exceeding the tolerance is not classified as bounded.
        """
        phi_vals = [100 - i for i in range(150)]
        # Inject a large excursion
        for i in range(50, 60):
            phi_vals[i] += (i - 50) * 2.0 # 20.0 increase

        phi_history = [LyapunovValue(total=v, energy_component=0, test_component=0, obligation_component=0, timestamp=time.time()) for v in phi_vals]
        excursions = detect_bounded_excursions(phi_history, window_size=30, excursion_tolerance=10.0)
        assert len(excursions) == 0

    def test_verify_martingale_convergence_converging(self):
        """
        Tests that a converging (supermartingale) trajectory is correctly identified.
        """
        # Create a trajectory with a clear negative drift
        np.random.seed(42)
        phi_vals = [1000 - i*0.1 - np.random.normal(0, 0.05) for i in range(200)]
        phi_history = [LyapunovValue(total=v, energy_component=0, test_component=0, obligation_component=0, timestamp=time.time()) for v in phi_vals]

        is_converging = verify_martingale_convergence(phi_history, warmup_period=50)
        assert is_converging

    def test_verify_martingale_convergence_not_converging(self):
        """
        Tests that a non-converging (random walk) trajectory is correctly identified.
        """
        # Create a random walk trajectory
        np.random.seed(42)
        phi_vals = [100 + np.sum(np.random.randn(i)) for i in range(1, 201)]
        phi_history = [LyapunovValue(total=v, energy_component=0, test_component=0, obligation_component=0, timestamp=time.time()) for v in phi_vals]

        is_converging = verify_martingale_convergence(phi_history, warmup_period=50)
        assert not is_converging

    def test_verify_martingale_convergence_insufficient_data(self):
        """
        Tests that the function returns False if there is not enough data.
        """
        phi_history = [LyapunovValue(total=100 - i, energy_component=0, test_component=0, obligation_component=0, timestamp=time.time()) for i in range(50)]
        is_converging = verify_martingale_convergence(phi_history, warmup_period=20)
        assert is_converging is False
