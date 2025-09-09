# Convergence Theory

The reliability of the QuantaCirc system hinges on its ability to predictably converge to a stable, low-energy state. This convergence is not merely an empirical observation but is backed by rigorous mathematical theories. This document details the key theoretical pillars that ensure system stability and convergence.

The primary tools used to formally reason about convergence in QuantaCirc are **Lyapunov stability theory** and the **Banach fixed-point theorem**.

## Lyapunov Stability

Lyapunov's second method for stability is used to analyze the stability of dynamical systems without explicitly solving the differential equations. In QuantaCirc, the system's state evolution is treated as a discrete-time dynamical system.

A **Lyapunov function**, `V(x)`, is a scalar function on the state space that is positive-definite and has a negative-definite forward difference. In our system, the "energy" function `E(s)` (or a related information-theoretic measure like entropy) serves as the Lyapunov function.

### Stability Condition

The system is guaranteed to converge to a stable fixed point if the Lyapunov function `V(x)` satisfies:

$$
\Delta V(x_t) = V(x_{t+1}) - V(x_t) < 0
$$

This condition means that the function `V` must strictly decrease with every state transition. The `core/lyapunov_monitor.py` is responsible for tracking this condition and ensuring that the system is always moving towards a more stable state. The formal proofs of these properties can be found in `proofs/coq/stability.v`.

## Banach Fixed-Point Theorem

The Banach fixed-point theorem provides a condition for the existence and uniqueness of a fixed point for a contractive mapping on a complete metric space. In the context of QuantaCirc, the state update process can be modeled as an operator `T` that maps the current state `s_t` to the next state `s_{t+1}`.

### Contractive Mapping

The operator `T` is a **contractive mapping** if there exists a constant `q` with `0 \le q < 1` such that for any two states `s_1` and `s_2`:

$$
d(T(s_1), T(s_2)) \le q \cdot d(s_1, s_2)
$$

Where `d` is a suitable distance metric on the state space (see `math_utils/distance_metrics.py`).

If the state update operator is a contractive map, the theorem guarantees that:
1. There exists a unique fixed point `s*` such that `T(s*) = s*`.
2. The sequence of states `s_t` will converge to `s*` regardless of the initial state.

The `math_utils/contractive_maps.py` module provides tools for verifying this property for the system's operators. The formal proofs related to this can be found in `proofs/coq/convergence.v`.

By combining these two powerful mathematical frameworks, QuantaCirc provides strong guarantees about the stability and convergence of its optimization processes.
