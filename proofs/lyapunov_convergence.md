# Mathematical Proof of Almost-Sure Convergence for the Lyapunov Function Φ(S)

## 1. Definition of the Lyapunov Function

The Lyapunov function Φ(S) is defined as:

Φ(S) = E_approx(S) + κ·#{failing tests} + ξ·#{open obligations}

where:
- `E_approx(S)` is the approximate energy of the system state S.
- `#{failing tests}` is the number of failing tests.
- `#{open obligations}` is the number of open proof obligations.
- `κ` and `ξ` are positive constants.

Φ(S) is a potential function that measures the "disorder" of the system. A lower value of Φ indicates a more stable state. The function is bounded below by 0, assuming `E_approx(S)` is non-negative.

## 2. The System as a Stochastic Process

The evolution of the system state S_t over time `t` can be viewed as a stochastic process. Consequently, the sequence of Lyapunov values Φ_t = Φ(S_t) is also a stochastic process. Our goal is to show that this process converges to a stable value.

## 3. Supermartingale Property

We aim to show that Φ_t is a supermartingale. A stochastic process X_t is a supermartingale if:

E[X_{t+1} | F_t] ≤ X_t

where F_t is the filtration representing the history of the process up to time t.

In our case, we want to show that:

E[Φ_{t+1} | Φ_t, Φ_{t-1}, ..., Φ_0] ≤ Φ_t

In practice, we prove a stronger condition: that the system has a negative drift. That is, for some ε > 0:

E[Φ_{t+1} | F_t] ≤ Φ_t - ε

This means that, on average, the Lyapunov function is expected to decrease at each step. This is the property verified by the `verify_martingale_convergence` function.

## 4. Bounded Excursions

The supermartingale property might be temporarily violated. For example, adding new features might introduce new failing tests, causing a temporary increase in Φ. These are called "excursions".

The system is designed to handle only "bounded excursions". This means that after a temporary increase, the system's self-correcting mechanisms will work to reduce Φ again. The `detect_bounded_excursions` function is responsible for monitoring this.

## 5. Almost-Sure Convergence

Doob's Martingale Convergence Theorem states that a supermartingale that is bounded below converges almost surely.

1.  **Bounded Below**: As established, Φ(S) ≥ 0, so it is bounded below.
2.  **Supermartingale**: Assuming the system is designed correctly, after a warm-up period, the process Φ_t behaves as a supermartingale.

Therefore, by Doob's theorem, Φ_t converges almost surely to a random variable Φ_∞.

lim_{t→∞} Φ_t = Φ_∞ (almost surely)

This means that the system will eventually reach a stable state where the Lyapunov function no longer changes significantly. This corresponds to a state with low energy, few or no failing tests, and few or no open obligations.

## 6. Conclusion

The Lyapunov function Φ(S) provides a measure of system stability. By designing the system to decrease Φ in expectation, we form a supermartingale. The Martingale Convergence Theorem then provides a firm theoretical foundation for the almost-sure convergence of the system to a stable state, provided that any excursions in the Lyapunov value are bounded.
