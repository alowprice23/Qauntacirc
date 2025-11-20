import numpy as np
from scipy import stats
from scipy.optimize import minimize

class Distribution:
    """Base class for probability distributions."""
    def __init__(self, params):
        self.params = params

    def pdf(self, x):
        raise NotImplementedError

    def cdf(self, x):
        raise NotImplementedError

    def sample(self, n):
        raise NotImplementedError

class Normal(Distribution):
    """Normal (Gaussian) distribution."""
    def __init__(self, mu=0, sigma=1):
        super().__init__({'mu': mu, 'sigma': sigma})
        self.dist = stats.norm(loc=mu, scale=sigma)

    def pdf(self, x):
        return self.dist.pdf(x)

    def cdf(self, x):
        return self.dist.cdf(x)

    def sample(self, n=1):
        return self.dist.rvs(size=n)

    @staticmethod
    def fit_mle(data):
        """Maximum Likelihood Estimation for Normal distribution."""
        mu = np.mean(data)
        sigma = np.std(data)
        return Normal(mu, sigma)

class Exponential(Distribution):
    """Exponential distribution."""
    def __init__(self, lambd=1):
        super().__init__({'lambda': lambd})
        self.dist = stats.expon(scale=1/lambd)

    def pdf(self, x):
        return self.dist.pdf(x)

    def cdf(self, x):
        return self.dist.cdf(x)

    def sample(self, n=1):
        return self.dist.rvs(size=n)

    @staticmethod
    def fit_mle(data):
        """Maximum Likelihood Estimation for Exponential distribution."""
        lambd = 1 / np.mean(data)
        return Exponential(lambd)

def goodness_of_fit_kstest(data, dist_class):
    """
    Performs a Kolmogorov-Smirnov test for goodness of fit.

    Args:
        data (np.ndarray): The observed data.
        dist_class (class): The distribution class to test against (e.g., Normal, Exponential).

    Returns:
        float: The K-S statistic.
        float: The p-value.
    """
    # Fit the distribution to the data
    fitted_dist = dist_class.fit_mle(data)

    # Perform the K-S test
    return stats.kstest(data, fitted_dist.dist.cdf)

def bayesian_estimation_normal(data, prior_mu, prior_sigma, n_samples=1000):
    """
    Performs Bayesian estimation for the mean of a Normal distribution
    with a known variance and a Normal prior on the mean.

    This is a simplified example. A full implementation would use MCMC methods.
    """
    # Assuming known variance, using sample variance for estimation
    sigma = np.std(data, ddof=1)
    if sigma == 0: sigma = 1e-9 # Avoid division by zero
    n = len(data)

    # Posterior parameters
    posterior_sigma_sq = 1 / (1/prior_sigma**2 + n/sigma**2)
    posterior_mu = posterior_sigma_sq * (prior_mu/prior_sigma**2 + np.sum(data)/sigma**2)

    # Sample from the posterior distribution
    posterior_samples = np.random.normal(posterior_mu, np.sqrt(posterior_sigma_sq), n_samples)
    return posterior_samples
