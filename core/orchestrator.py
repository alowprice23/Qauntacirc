import time
import numpy as np
import scipy.stats as stats
from typing import List
from core.types import TelemetryData, RiskUpdate, CoverageReport, ErrorEvent

class Orchestrator:
    def __init__(self):
        self.current_empirical_risk = 0.0
        # CUSUM parameters
        self.cusum = 0.0
        self.baseline_rate = 0.01 # Should be initialized with historical data
        self.detection_threshold = 5.0
        # Bayesian update parameters
        self.prior_alpha = 1.0 # Assume a non-informative prior initially
        self.prior_beta = 1.0

    def update_risk_from_telemetry(self,
                                  telemetry_data: TelemetryData,
                                  window_minutes: int = 60) -> RiskUpdate:
        """
        Update empirical risk bounds from live system telemetry
        using change-point detection and Bayesian updating
        """

        # Extract relevant metrics from telemetry
        error_events = telemetry_data.extract_error_events(window_minutes)
        total_requests = telemetry_data.extract_request_count(window_minutes)

        if total_requests == 0:
            return RiskUpdate(risk_delta=0.0, confidence=0.0)

        # Observed error rate in current window
        # This is not how CUSUM is typically used, but following prompt structure
        change_detected = self._detect_change_point_batch(error_events, total_requests)

        if change_detected:
            # Inflate risk bounds due to detected change
            current_error_rate = len(error_events) / total_requests
            risk_inflation = self._compute_risk_inflation(current_error_rate)

            return RiskUpdate(
                risk_delta=risk_inflation,
                confidence=0.95,
                reason="Change point detected in error rate",
                expiry_time=time.time() + 3600,  # 1 hour inflation
                decay_factor=0.95  # Exponential decay
            )

        # Bayesian update of prior belief
        posterior_alpha = self.prior_alpha + len(error_events)
        posterior_beta = self.prior_beta + total_requests - len(error_events)

        # Compute credible interval for true error rate
        credible_upper_bound = stats.beta.ppf(0.95, posterior_alpha, posterior_beta)

        risk_delta = credible_upper_bound - self.current_empirical_risk
        self.current_empirical_risk = credible_upper_bound

        # Update priors for next iteration
        self.prior_alpha = posterior_alpha
        self.prior_beta = posterior_beta

        return RiskUpdate(
            risk_delta=risk_delta,
            confidence=0.95,
            reason="Bayesian update from telemetry",
            posterior_params=(posterior_alpha, posterior_beta)
        )

    def _detect_change_point_batch(self, error_events: List[ErrorEvent], total_requests: int) -> bool:
        """
        Detect change points in error rate using CUSUM algorithm on a batch.
        """
        if total_requests < 30: # Need enough data to be meaningful
            return False

        error_rate = len(error_events) / total_requests

        # Simple CUSUM: accumulate deviation from baseline
        self.cusum = max(0, self.cusum + (error_rate - self.baseline_rate))
        if self.cusum > self.detection_threshold:
            return True

        return False

    def _compute_risk_inflation(self, current_error_rate: float) -> float:
        # Mock implementation for risk inflation
        return current_error_rate * 1.5

    def adjust_risk_for_coverage(self,
                           base_risk: float,
                           coverage_report: CoverageReport) -> float:
        """
        Adjust risk bounds based on test coverage using coverage-adjusted Chernoff bounds
        """

        line_coverage = coverage_report.line_coverage / 100.0 if coverage_report.line_coverage > 1.0 else coverage_report.line_coverage
        branch_coverage = coverage_report.branch_coverage / 100.0 if coverage_report.branch_coverage > 1.0 else coverage_report.branch_coverage
        overall_coverage = coverage_report.overall_coverage / 100.0 if coverage_report.overall_coverage > 1.0 else coverage_report.overall_coverage

        # Coverage-adjusted sample size
        effective_n = line_coverage * coverage_report.total_tests
        branch_coverage_factor = np.sqrt(branch_coverage)

        adjusted_n = effective_n * branch_coverage_factor

        # Residual risk from uncovered code paths
        uncovered_fraction = 1.0 - overall_coverage
        residual_risk = uncovered_fraction * 0.01  # Conservative estimate

        # Recompute Chernoff bound with adjusted parameters
        if adjusted_n > 0:
            epsilon = np.sqrt(-np.log(base_risk / 2) / (2 * adjusted_n)) if base_risk < 2 else 0
            coverage_adjusted_bound = 2 * np.exp(-2 * adjusted_n * epsilon**2)
        else:
            coverage_adjusted_bound = 1.0

        return coverage_adjusted_bound + residual_risk
