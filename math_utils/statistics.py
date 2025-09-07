import numpy as np
from scipy import stats

def robust_mean(data, trim_fraction=0.1):
    """
    Computes the trimmed mean, a robust estimator of central tendency.

    Args:
        data (np.ndarray): The input data.
        trim_fraction (float): The fraction of data to trim from each end.

    Returns:
        float: The trimmed mean.
    """
    return stats.trim_mean(data, trim_fraction)

def t_test_one_sample(data, popmean):
    """
    Performs a one-sample t-test.

    Args:
        data (np.ndarray): The sample data.
        popmean (float): The population mean to test against.

    Returns:
        float: The t-statistic.
        float: The p-value.
    """
    return stats.ttest_1samp(data, popmean)

def mann_whitney_u_test(x, y):
    """
    Performs the Mann-Whitney U test, a non-parametric test for comparing two samples.

    Args:
        x (np.ndarray): The first sample.
        y (np.ndarray): The second sample.

    Returns:
        float: The U statistic.
        float: The p-value.
    """
    return stats.mannwhitneyu(x, y)

def bonferroni_correction(p_values):
    """
    Applies the Bonferroni correction for multiple hypothesis testing.

    Args:
        p_values (list or np.ndarray): The list of p-values.

    Returns:
        np.ndarray: The corrected p-values.
    """
    p_values = np.asarray(p_values)
    return np.minimum(1.0, p_values * len(p_values))

def fdr_correction(p_values, alpha=0.05):
    """
    Applies the Benjamini-Hochberg False Discovery Rate (FDR) correction.

    Args:
        p_values (list or np.ndarray): The list of p-values.
        alpha (float): The desired FDR level.

    Returns:
        np.ndarray: A boolean array indicating which p-values are significant.
        np.ndarray: The corrected p-values (q-values).
    """
    p_values = np.asarray(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_p_values = p_values[sorted_indices]

    m = len(p_values)
    threshold = (np.arange(1, m + 1) / m) * alpha

    significant = sorted_p_values <= threshold

    # Find the largest p-value that is significant
    if np.any(significant):
        max_sig_idx = np.where(significant)[0][-1]
        final_threshold = sorted_p_values[max_sig_idx]
        significant_indices = sorted_indices[p_values <= final_threshold]
    else:
        significant_indices = []

    # This is a simplified return, statsmodels provides a more complete one
    return significant_indices


def bootstrap(data, n_bootstrap=1000, func=np.mean):
    """
    Performs bootstrap resampling to estimate the sampling distribution of a statistic.

    Args:
        data (np.ndarray): The input data.
        n_bootstrap (int): The number of bootstrap samples.
        func (callable): The statistic to compute on each sample.

    Returns:
        np.ndarray: An array of the computed statistic from each bootstrap sample.
    """
    n = len(data)
    bootstrap_stats = np.zeros(n_bootstrap)
    for i in range(n_bootstrap):
        sample = np.random.choice(data, size=n, replace=True)
        bootstrap_stats[i] = func(sample)
    return bootstrap_stats

def jackknife_estimate(data, func=np.mean):
    """
    Performs jackknife resampling to estimate the bias and variance of a statistic.

    Args:
        data (np.ndarray): The input data.
        func (callable): The statistic to compute.

    Returns:
        float: The jackknife estimate of the statistic.
        float: The jackknife estimate of the bias.
        float: The jackknife estimate of the variance.
    """
    n = len(data)
    theta_hat = func(data)
    jackknife_stats = np.zeros(n)

    for i in range(n):
        jackknife_sample = np.delete(data, i)
        jackknife_stats[i] = func(jackknife_sample)

    mean_jackknife_stat = np.mean(jackknife_stats)

    bias = (n - 1) * (mean_jackknife_stat - theta_hat)
    variance = (n - 1) / n * np.sum((jackknife_stats - mean_jackknife_stat)**2)

    return theta_hat - bias, bias, variance
