# Mathematical Foundations

The QuantaCirc system is built upon a solid foundation of principles from statistical mechanics, information theory, and quantum-inspired optimization. This document outlines the core mathematical concepts that underpin the system's behavior.

## Statistical Mechanics & Annealing

The core optimization algorithm in QuantaCirc is based on **Simulated Annealing**, a probabilistic technique for approximating the global optimum of a given function. The system state is analogous to the state of a physical system, and the objective function is analogous to the system's "energy".

### The Boltzmann Distribution

The probability of the system being in a state `s` with energy `E(s)` at a temperature `T` is given by the Boltzmann distribution:

$$
P(s) = \frac{1}{Z(T)} e^{-\frac{E(s)}{kT}}
$$

Where:
- `E(s)` is the energy of state `s`.
- `T` is the temperature.
- `k` is the Boltzmann constant.
- `Z(T)` is the partition function, which normalizes the probability distribution:
  $$
  Z(T) = \sum_{s} e^{-\frac{E(s)}{kT}}
  $$

The system uses a **two-phase annealing** process (`core/two_phase_annealer.py`) to carefully control the temperature `T`, allowing the system to explore the state space broadly at high temperatures and converge to a low-energy state as the temperature decreases.

## Information Theory

Information theory provides tools to quantify uncertainty and information content. These are used in QuantaCirc to guide the search process and measure the convergence of the system.

### Shannon Entropy

The uncertainty of the system's state distribution is measured by the Shannon entropy:

$$
H = - \sum_{s} P(s) \log P(s)
$$

The `math_utils/info_entropy.py` module provides functions for calculating entropy, which is used by the `lyapunov_monitor` to track convergence.

## Quantum-Inspired Concepts

While not a true quantum simulator, QuantaCirc draws inspiration from quantum mechanics to explore complex state spaces. The concept of a "state space" (`core/state_space.py`) can be thought of as a Hilbert space, where each possible configuration of the system is a basis vector. System evolution is guided by operators that act on this state space.

This approach allows for a richer representation of the problem and more sophisticated exploration strategies than classical optimization methods alone. The `math_utils/graph_spectra.py` and `math_utils/laplacian.py` modules are used to analyze the structure of this state space.
