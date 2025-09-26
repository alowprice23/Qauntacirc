import abc
from typing import List, Any

from core.types import QCState as State, AgentResult as Action
from core.constraint_solver import SMTConstraintSolver
from math_utils.lyapunov import is_lyapunov_stable
from core.closure_rules import ClosureRule

class Condition(abc.ABC):
    """Abstract base class for a single condition within a contract."""

    @abc.abstractmethod
    def check(self, *args, **kwargs) -> bool:
        """Evaluates the condition."""
        pass


class Contract:
    """
    A contract specifies a set of pre- and post-conditions that an agent's
    execution must satisfy.
    """
    def __init__(self, name: str, preconditions: List[Condition], postconditions: List[Condition]):
        self.name = name
        self.preconditions = preconditions
        self.postconditions = postconditions

    def check_preconditions(self, state: "State") -> bool:
        """Checks if all preconditions are met for the current state."""
        return all(cond.check(state=state) for cond in self.preconditions)

    def check_postconditions(self, state: "State", action: "Action") -> bool:
        """Checks if all postconditions are met after an action is taken."""
        return all(cond.check(state=state, action=action) for cond in self.postconditions)


class EnergyCondition(Condition):
    """
    Condition to check if the system's energy state is within allowed bounds.
    """
    def __init__(self, solver: "SMTConstraintSolver", max_energy: float):
        self.solver = solver
        self.max_energy = max_energy

    def check(self, state: "State", **kwargs) -> bool:
        """
        Verifies that the current energy state is below the maximum threshold
        using the provided SMT solver.
        """
        if not hasattr(state, 'energy'):
            return False

        # Use a temporary context in the solver to check the condition.
        self.solver.solver.push()
        try:
            # Declare the variable we'll be constraining. It's idempotent.
            self.solver.declare_variable('energy', 'Real')
            # Add a temporary constraint that the 'energy' variable equals the current state's energy.
            self.solver.add_constraint(f"energy == {state.energy}")
            # Check if the property holds given this temporary fact.
            result = self.solver.check_property(f"energy <= {self.max_energy}")
        finally:
            # Important: remove the temporary constraint.
            self.solver.solver.pop()

        return result


class LyapunovCondition(Condition):
    """
    Condition to ensure that a proposed action maintains Lyapunov stability.
    """
    def __init__(self, stability_func=is_lyapunov_stable):
        self.stability_func = stability_func

    def check(self, state: "State", action: "Action", **kwargs) -> bool:
        """
        Verifies that the action does not violate system stability.
        This is typically a post-condition.
        """
        if not hasattr(state, 'quantum_state') or state.quantum_state is None or not hasattr(state.quantum_state, 'state_vector'):
            return False

        delta_vector = action.result.get("delta_vector", [0] * len(state.quantum_state.state_vector)) if hasattr(action, 'result') and action.result else [0] * len(state.quantum_state.state_vector)
        new_state_vector = [x + y for x, y in zip(state.quantum_state.state_vector, delta_vector)]
        return self.stability_func(new_state_vector)


class ClosureRuleCondition(Condition):
    """
    Condition to enforce domain-specific closure rules.
    """
    def __init__(self, rule: "ClosureRule"):
        self.rule = rule

    def check(self, state: "State", action: "Action", **kwargs) -> bool:
        """
        Verifies that the action complies with a given closure rule.
        This is typically a post-condition.
        """
        return self.rule.is_satisfied(state, action)
