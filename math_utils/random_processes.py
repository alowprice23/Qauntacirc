import numpy as np
from statsmodels.tsa.stattools import adfuller

def rbf_kernel(x1, x2, length_scale=1.0, sigma_f=1.0):
    """Radial Basis Function (RBF) kernel for Gaussian Processes."""
    sqdist = np.sum(x1**2, 1).reshape(-1, 1) + np.sum(x2**2, 1) - 2 * np.dot(x1, x2.T)
    return sigma_f**2 * np.exp(-0.5 / length_scale**2 * sqdist)

class GaussianProcess:
    """A simple Gaussian Process regressor."""
    def __init__(self, kernel=rbf_kernel):
        self.kernel = kernel
        self.X_train = None
        self.y_train = None
        self.K = None

    def fit(self, X, y):
        self.X_train = X
        self.y_train = y
        self.K = self.kernel(X, X)

    def predict(self, X_test):
        if self.X_train is None:
            raise RuntimeError("The GP must be fitted before making predictions.")

        K_s = self.kernel(self.X_train, X_test)
        K_ss = self.kernel(X_test, X_test)

        K_inv = np.linalg.inv(self.K)

        mu_s = K_s.T.dot(K_inv).dot(self.y_train)
        cov_s = K_ss - K_s.T.dot(K_inv).dot(K_s)

        return mu_s, np.diag(cov_s)

def generate_brownian_motion(n_steps, dt=0.01):
    """Generates a 1D Brownian motion path."""
    W = np.zeros(n_steps)
    for i in range(1, n_steps):
        W[i] = W[i-1] + np.random.normal(0, np.sqrt(dt))
    return W

def estimate_spectral_density(time_series, method='periodogram'):
    """
    Estimates the spectral density of a time series.

    Args:
        time_series (np.ndarray): The input time series data.
        method (str): The method to use ('periodogram' or 'welch').

    Returns:
        np.ndarray: Frequencies.
        np.ndarray: Power spectral density.
    """
    if method == 'periodogram':
        n = len(time_series)
        freq = np.fft.fftfreq(n)
        psd = np.abs(np.fft.fft(time_series))**2 / n
        return freq[:n//2], psd[:n//2]
    else:
        # A full implementation would use scipy.signal.welch
        raise NotImplementedError("Welch's method is not implemented here.")

def test_stationarity(time_series):
    """
    Performs the Augmented Dickey-Fuller test for stationarity.

    Args:
        time_series (np.ndarray): The time series to test.

    Returns:
        bool: True if the series is stationary, False otherwise.
        float: The p-value of the test.
    """
    result = adfuller(time_series)
    p_value = result[1]
    return p_value <= 0.05, p_value
