---
generation_method: "This document is intended to be auto-generated from the Python docstrings in the `/agents` directory using a tool like `mkdocstrings`. The content below is a manually-created placeholder."
---

# API Reference: `agents`

This document provides a reference for the base agent contract and the available agent implementations. Agents are the primary actors in the QuantaCirc system, responsible for proposing and executing state transitions.

## `BaseAgent`

**`agents.base.agent.BaseAgent`**

The abstract base class for all agents. All custom agents must inherit from this class and implement its methods.

### Abstract Methods

#### `propose_transition(state: State) -> Transition`

Proposes a new state transition based on the current state.

- **Parameters**:
    - `state` (`State`): The current state of the system.
- **Returns**:
    - `Transition`: The proposed transition.

#### `execute_transition(transition: Transition) -> State`

Executes a given transition and returns the new state.

- **Parameters**:
    - `transition` (`Transition`): The transition to execute.
- **Returns**:
    - `State`: The new state after executing the transition.

---

## Example Agent: `PauliGuardAgent`

**`agents.pauli_guard.agent.PauliGuardAgent`**

An agent that uses principles from quantum computing (Pauli matrices) to guard against certain types of errors.

### Configuration

The `PauliGuardAgent` is configured with a specific set of Pauli operators to monitor.

- **`operators`**: A list of strings, e.g., `["X", "Y", "Z"]`.

### Behavior

This agent monitors the system state for deviations that would violate the symmetries defined by its configured Pauli operators. If it detects a potential violation, it proposes a corrective transition to restore the symmetry. This is particularly useful for maintaining the integrity of quantum-inspired computations.
