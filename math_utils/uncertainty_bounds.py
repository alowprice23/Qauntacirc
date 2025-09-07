import numpy as np
import math
from scipy.stats import norm

def hoeffding_inequality(n, t, bounds=None, data=None):
    """
    Calculates the probability bound using Hoeffding's inequality.
    P(|S_n/n - E[X]| >= t) <= 2 * exp(-2 * n * t^2 / (b-a)^2) for X in [a,b]

    Args:
        n (int): The number of samples.
        t (float): The deviation threshold.
        bounds (tuple, optional): The (a, b) bounds of the random variables.
        data (np.ndarray, optional): If provided, bounds are inferred from data.

    Returns:
        float: The upper bound on the probability of deviation.
    """
    if bounds is None:
        if data is None:
            raise ValueError("Either 'bounds' or 'data' must be provided.")
        a, b = np.min(data), np.max(data)
    else:
        a, b = bounds

    if n <= 0 or t <= 0:
        return 1.0

    return 2 * np.exp(-2 * n * t**2 / (b - a)**2)

def chernoff_bound_bernoulli(n, p, a):
    """
    Calculates the Chernoff bound for a sum of Bernoulli random variables.
    P(S_n >= a*n) <= exp(-n * D(a || p)) where D is KL-divergence.

    Args:
        n (int): The number of Bernoulli trials.
        p (float): The probability of success for each trial.
        a (float): The target average (a > p).

    Returns:
        float: The upper bound on the probability.
    """
    if a <= p:
        return 1.0

    # KL divergence for Bernoulli variables: D(a || p)
    kl_div = a * math.log(a / p) + (1 - a) * math.log((1 - a) / (1 - p))
    return np.exp(-n * kl_div)


def bennett_inequality(n, t, sigma_sq, b):
    """
    Calculates the probability bound using Bennett's inequality.
    P(S_n/n - E[X] >= t) <= exp(-n*sigma^2/b^2 * h(b*t/sigma^2))
    where h(u) = (1+u)log(1+u) - u

    Args:
        n (int): Number of samples.
        t (float): Deviation threshold.
        sigma_sq (float): Variance of the random variables.
        b (float): Upper bound on the random variables.

    Returns:
        float: The upper bound on the probability of deviation.
    """
    if t <= 0:
        return 1.0

    def h(u):
        return (1 + u) * np.log(1 + u) - u

    nu = n * sigma_sq / b**2
    u = b * t / sigma_sq

    return np.exp(-nu * h(u))

def bootstrap_confidence_interval(data, n_bootstrap=1000, alpha=0.05):
    """
    Computes a bootstrap confidence interval for the mean of a dataset.

    Args:
        data (np.ndarray): The input data.
        n_bootstrap (int): The number of bootstrap samples to generate.
        alpha (float): The significance level.

    Returns:
        tuple: The (lower, upper) bounds of the confidence interval.
    """
    n = len(data)
    bootstrap_means = np.zeros(n_bootstrap)
    for i in range(n_bootstrap):
        sample = np.random.choice(data, size=n, replace=True)
        bootstrap_means[i] = np.mean(sample)

    lower_bound = np.percentile(bootstrap_means, 100 * (alpha / 2))
    upper_bound = np.percentile(bootstrap_means, 100 * (1 - alpha / 2))

    return lower_bound, upper_bound

class UncertaintyQuantifier:
    def __init__(self, data):
        self.data = np.asarray(data)
        self.n = len(data)
        self.mean = np.mean(data)
        self.std_dev = np.std(data)

    def get_confidence_bounds(self, confidence_level=0.95):
        """Returns confidence bounds for the mean."""
        z_score = norm.ppf(1 - (1 - confidence_level) / 2)
        margin_of_error = z_score * (self.std_dev / np.sqrt(self.n))
        return self.mean - margin_of_error, self.mean + margin_of_error

class ConfidenceBounds:
    def __init__(self, lower, upper):
        self.lower = lower
        self.upper = upper

    def __repr__(self):
        return f"ConfidenceBounds(lower={self.lower:.4f}, upper={self.upper:.4f})"
