import numpy as np

def autocorrelation_function(time_series, max_lag=None):
    """
    Computes the autocorrelation function (ACF) of a time series.

    Args:
        time_series (np.ndarray): The input time series data.
        max_lag (int, optional): The maximum lag to compute. Defaults to n-1.

    Returns:
        np.ndarray: The autocorrelation for lags 0 to max_lag.
    """
    n = len(time_series)
    if max_lag is None:
        max_lag = n - 1

    mean = np.mean(time_series)
    var = np.var(time_series)

    acf = np.zeros(max_lag + 1)

    for lag in range(max_lag + 1):
        if lag == 0:
            acf[lag] = 1.0
            continue

        # Covariance at lag k
        cov = np.sum((time_series[:n-lag] - mean) * (time_series[lag:] - mean))
        acf[lag] = cov / (n * var)

    return acf

def green_kubo_integral(correlation_function, dt):
    """
    Integrates a time correlation function to get a transport coefficient.

    The Green-Kubo formula is of the form:
    gamma = integral from 0 to inf of <A(0)A(t)> dt

    Args:
        correlation_function (np.ndarray): The time correlation function values.
        dt (float): The time step between correlation function values.

    Returns:
        float: The estimated transport coefficient.
    """
    # Simple numerical integration (trapezoidal rule)
    integral = np.trapz(correlation_function, dx=dt)
    return integral

def calculate_diffusion_coefficient(velocity_acf, dt):
    """
    Calculates the self-diffusion coefficient from the velocity autocorrelation function.

    D = (1/d) * integral from 0 to inf of <v(0) . v(t)> dt
    where d is the number of dimensions.

    Args:
        velocity_acf (np.ndarray): The velocity autocorrelation function.
        dt (float): The time step.

    Returns:
        float: The diffusion coefficient.
    """
    # Assuming 3 dimensions for this example
    d = 3
    return (1 / d) * green_kubo_integral(velocity_acf, dt)

def calculate_shear_viscosity(stress_tensor_acf, volume, temperature, dt):
    """
    Calculates shear viscosity from the stress tensor autocorrelation function.

    eta = (V / (k_B * T)) * integral of <P_xy(0)P_xy(t)> dt

    Args:
        stress_tensor_acf (np.ndarray): The ACF of an off-diagonal component of the
                                        pressure tensor (e.g., P_xy).
        volume (float): The volume of the system.
        temperature (float): The temperature of the system.
        dt (float): The time step.

    Returns:
        float: The shear viscosity.
    """
    k_B = 1.380649e-23 # Boltzmann constant in J/K

    prefactor = volume / (k_B * temperature)
    integral = green_kubo_integral(stress_tensor_acf, dt)

    return prefactor * integral
