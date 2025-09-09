---
generation_method: "This document is intended to be auto-generated from the Python docstrings in the `/core` directory using a tool like `mkdocstrings`. The content below is a manually-created placeholder."
---

# API Reference: `core`

This document provides a reference for the key classes and functions within the `core` module. The `core` module contains the fundamental building blocks of the QuantaCirc system.

## `ConvergenceEngine`

**`core.convergence_engine.ConvergenceEngine`**

The main engine that drives the system's state towards convergence.

### Methods

#### `run(initial_state: State, max_steps: int) -> State`

Runs the convergence process starting from an `initial_state`.

- **Parameters**:
    - `initial_state` (`State`): The starting state for the simulation.
    - `max_steps` (`int`): The maximum number of steps to run the simulation for.
- **Returns**:
    - `State`: The final, converged state.

---

## `ConstraintSolver`

**`core.constraint_solver.ConstraintSolver`**

A class responsible for checking and enforcing the system's constraints (see Δ-Closure rules).

### Methods

#### `is_valid(state: State, proposed_transition: Transition) -> bool`

Checks if a `proposed_transition` from the current `state` is valid.

- **Parameters**:
    - `state` (`State`): The current state of the system.
    - `proposed_transition` (`Transition`): The transition to be checked.
- **Returns**:
    - `bool`: `True` if the transition is valid, `False` otherwise.

---

## `TwoPhaseAnnealer`

**`core.two_phase_annealer.TwoPhaseAnnealer`**

Manages the two-phase simulated annealing schedule.

### Methods

#### `get_temperature(step: int) -> float`

Calculates the temperature for a given `step` in the annealing process.

- **Parameters**:
    - `step` (`int`): The current step number.
- **Returns**:
    - `float`: The temperature for the given step.

---

## `EnergyCalculator`

**`core.energy_calculator.EnergyCalculator`**

Calculates the energy of a given system state.

### Methods

#### `calculate(state: State) -> float`

Computes the energy for the given `state`.

- **Parameters**:
    - `state` (`State`): The state to calculate the energy for.
- **Returns**:
    - `float`: The calculated energy of the state.
