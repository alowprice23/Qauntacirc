import numpy as np
from scipy.optimize import minimize

def maximum_likelihood_estimator(data, log_likelihood_func, initial_params):
    """
    Generic Maximum Likelihood Estimator (MLE).

    Args:
        data (np.ndarray): The observed data.
        log_likelihood_func (callable): A function that takes parameters and data,
                                       and returns the log-likelihood.
        initial_params (np.ndarray): Initial guess for the parameters.

    Returns:
        np.ndarray: The estimated parameters that maximize the log-likelihood.
    """
    # We minimize the negative log-likelihood
    objective = lambda params: -log_likelihood_func(params, data)

    result = minimize(objective, initial_params, method='L-BFGS-B')

    if not result.success:
        raise RuntimeError(f"MLE optimization failed: {result.message}")

    return result.x

def huber_rho(u, c=1.345):
    """Huber's rho function, the integral of the psi function."""
    abs_u = np.abs(u)
    return np.where(abs_u <= c, 0.5 * u**2, c * abs_u - 0.5 * c**2)

def m_estimator(data, rho_func, initial_param):
    """
    Generic M-estimator for a single parameter.

    M-estimators are a generalization of MLEs that are robust to outliers.
    They minimize sum(rho((x_i - theta) / s)), where rho is a robust loss function.

    Args:
        data (np.ndarray): The observed data.
        rho_func (callable): The robust loss function (e.g., Huber's rho).
        initial_param (float): Initial guess for the parameter.

    Returns:
        float: The estimated parameter.
    """
    # The scale 's' is often estimated robustly, e.g., using MAD.
    s = np.median(np.abs(data - np.median(data))) * 1.4826
    if s == 0:
        s = 1.0 # Avoid division by zero if all data points are the same

    objective = lambda theta: np.sum(rho_func((data - theta) / s))

    result = minimize(objective, initial_param)

    return result.x[0]

def huber_psi(u, c=1.345):
    """Huber's psi function for M-estimation."""
    return np.clip(u, -c, c)

def bias_variance_decomposition(estimator, true_param, data_generator, n_simulations=100, n_samples=50):
    """
    Performs bias-variance decomposition for an estimator.

    Args:
        estimator (callable): A function that takes data and returns a parameter estimate.
        true_param (float): The true parameter value.
        data_generator (callable): A function that generates a dataset of size n_samples.
        n_simulations (int): Number of simulations to run.
        n_samples (int): Number of samples in each dataset.

    Returns:
        float: The squared bias.
        float: The variance.
        float: The mean squared error (MSE).
    """
    estimates = np.zeros(n_simulations)
    for i in range(n_simulations):
        data = data_generator(n_samples)
        estimates[i] = estimator(data)

    mean_estimate = np.mean(estimates)

    bias = mean_estimate - true_param
    variance = np.var(estimates)
    mse = np.mean((estimates - true_param)**2)

    # mse should be approx bias^2 + variance
    return bias**2, variance, mse
