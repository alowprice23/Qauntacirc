import numpy as np
from pydantic import BaseModel
from typing import List

class ConfidenceBounds(BaseModel):
    lower: float
    upper: float
    confidence_level: float

class UncertaintyQuantifier:
    """A container for uncertainty quantification methods."""

    @staticmethod
    def chernoff_bound(n, epsilon):
        """
        Calculates the Chernoff bound for the probability of a deviation from the mean.
        P(S_n/n - p > epsilon) <= exp(-2 * n * epsilon^2)
        """
        if n <= 0 or epsilon < 0:
            return 1.0
        return np.exp(-2 * n * epsilon**2)

    @staticmethod
    def hoeffding_bound(n, epsilon):
        """
        Calculates the Hoeffding bound for the probability of a deviation from the mean.
        P(|S_n/n - p| > epsilon) <= 2 * exp(-2 * n * epsilon^2)
        """
        if n <= 0 or epsilon < 0:
            return 1.0
        return 2 * np.exp(-2 * n * epsilon**2)

    @staticmethod
    def hoeffding_inequality(data: List[float], confidence: float = 0.95) -> ConfidenceBounds:
        """
        Computes the confidence interval for the mean of a bounded variable
        using Hoeffding's inequality.
        """
        n = len(data)
        if n == 0:
            return ConfidenceBounds(lower=-np.inf, upper=np.inf, confidence_level=confidence)

        mean = np.mean(data)
        range_val = np.max(data) - np.min(data)

        # alpha = 1 - confidence
        # P(|mean - E[mean]| >= epsilon) <= 2 * exp(-2 * n * epsilon^2 / (b-a)^2)
        # We solve for epsilon
        alpha = 1 - confidence
        if alpha <= 0 or alpha >= 2:
            return ConfidenceBounds(lower=-np.inf, upper=np.inf, confidence_level=confidence)

        epsilon = range_val * np.sqrt(np.log(2 / alpha) / (2 * n))

        return ConfidenceBounds(
            lower=mean - epsilon,
            upper=mean + epsilon,
            confidence_level=confidence
        )
