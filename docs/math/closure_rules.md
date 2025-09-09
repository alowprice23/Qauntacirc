# Mathematical Closure Rules (Δ-Closure)

In the QuantaCirc system, it is crucial to ensure that the state space remains well-behaved and that all operations are logically sound and physically meaningful. The **Mathematical Closure Rules**, collectively known as the **Δ-Closure** framework, provide a formal mechanism for enforcing these constraints.

The concept of "closure" here means that if you start with a valid state and apply a valid operation, the resulting state must also be valid. The Δ-Closure rules are a set of logical and mathematical constraints that are checked at every step of the system's evolution. These rules are implemented in the `core/closure_rules.py` module.

## The Δ Operator

The core of the framework is the **Δ operator**. This operator takes the current system state `S_t` and a proposed state transition `T` and returns a boolean value indicating whether the transition is valid.

$$
\Delta(S_t, T) \rightarrow \{\text{true}, \text{false}\}
$$

A transition is considered valid if and only if it satisfies all the defined closure rules.

## Key Closure Rules

The Δ-Closure framework includes several categories of rules that govern different aspects of the system's behavior.

### 1. Topological Closure

These rules ensure that the system's state remains within a "safe" or "valid" region of the state space. For example, a rule might prevent the system from entering a state with infinite energy.

Let `V` be the set of all valid states. For any state `s \in V` and any transition `T`, the resulting state `s' = T(s)` must also be in `V`.

$$
\forall s \in V, \forall T \in \mathcal{T} : T(s) \in V
$$

### 2. Conservation Laws

These rules enforce physical or logical conservation laws. For example, in a closed system, the total energy must be conserved, or the total number of particles must remain constant.

Let `C(s)` be a function that computes a conserved quantity for a state `s`. A conservation rule would be:

$$
C(s_t) = C(s_{t+1})
$$

### 3. Causal Closure

These rules ensure that the system's evolution respects causality. An effect cannot precede its cause. In a computational system, this often translates to rules about data dependencies. A task cannot execute until its inputs are available.

If task `B` depends on the output of task `A`, then:

$$
\text{timestamp}(B) > \text{timestamp}(A)
$$

## Formal Verification

The correctness of these closure rules is critical for the overall reliability of the system. Some of these rules are formally verified using the SMT solver Z3. The SMT definitions for these constraints can be found in `proofs/smt/constraints.smt2`.

By enforcing these closure rules at every step, the QuantaCirc system can guarantee that its operation remains within the bounds of mathematical and logical consistency, preventing a wide range of potential errors and instabilities.
