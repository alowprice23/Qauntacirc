import numpy as np

def metropolis_hastings_sampler(target_pdf, proposal_dist, n_samples, initial_state, burn_in=100):
    """
    A generic Metropolis-Hastings MCMC sampler.

    Args:
        target_pdf (callable): The (unnormalized) probability density function of the target distribution.
        proposal_dist (callable): A function that proposes a new state given the current state.
        n_samples (int): The number of samples to generate.
        initial_state (np.ndarray): The starting point for the sampler.
        burn_in (int): The number of initial samples to discard.

    Returns:
        np.ndarray: An array of samples from the target distribution.
    """
    samples = np.zeros((n_samples, len(initial_state)))
    current_state = initial_state

    for i in range(n_samples + burn_in):
        proposed_state = proposal_dist(current_state)

        # Acceptance probability
        acceptance_prob = min(1, target_pdf(proposed_state) / target_pdf(current_state))

        if np.random.rand() < acceptance_prob:
            current_state = proposed_state

        if i >= burn_in:
            samples[i - burn_in] = current_state

    return samples

def importance_sampling(target_pdf, proposal_pdf, proposal_sampler, n_samples):
    """
    Performs importance sampling to estimate the expectation of a function.

    This function returns the weighted samples, which can be used to estimate E[f(x)].
    E[f(x)] approx= sum(w_i * f(x_i)) / sum(w_i)

    Args:
        target_pdf (callable): The target probability density function.
        proposal_pdf (callable): The proposal probability density function.
        proposal_sampler (callable): A function that draws samples from the proposal dist.
        n_samples (int): The number of samples to draw.

    Returns:
        np.ndarray: The samples drawn from the proposal distribution.
        np.ndarray: The corresponding importance weights.
    """
    samples = proposal_sampler(n_samples)
    weights = target_pdf(samples) / proposal_pdf(samples)
    return samples, weights

def stratified_sampling(strata_sampler, strata_weights, n_samples):
    """
    Performs stratified sampling.

    Args:
        strata_sampler (list of callables): A list of functions, each sampling from a stratum.
        strata_weights (list of floats): The proportion of the population in each stratum.
        n_samples (int): The total number of samples to draw.

    Returns:
        np.ndarray: The collected samples.
    """
    n_strata = len(strata_sampler)
    samples_per_stratum = np.round(np.array(strata_weights) * n_samples).astype(int)

    all_samples = []
    for i in range(n_strata):
        stratum_samples = strata_sampler[i](samples_per_stratum[i])
        all_samples.append(stratum_samples)

    return np.concatenate(all_samples)

def latin_hypercube_sampling(n_samples, n_dims):
    """
    Generates samples using Latin Hypercube Sampling.

    Args:
        n_samples (int): The number of samples to generate.
        n_dims (int): The number of dimensions of the sample space.

    Returns:
        np.ndarray: An array of shape (n_samples, n_dims) with samples in [0,1].
    """
    # Create the grid
    grid = np.linspace(0, 1, n_samples + 1)

    # Generate random points within each interval
    samples = np.zeros((n_samples, n_dims))
    for i in range(n_dims):
        points = np.random.uniform(grid[:-1], grid[1:], n_samples)
        np.random.shuffle(points)
        samples[:, i] = points

    return samples
