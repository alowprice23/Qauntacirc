# core/closure_rules.py

"""
Manages and validates state transition consistency rules (Closure Rules).

This module ensures that any transformation between two system states
abides by a predefined set of rules, maintaining system integrity and
preventing invalid states.
"""

from __future__ import annotations

from typing import List, Callable, Dict, Any, Tuple

from core.types import QCState, ConstraintViolation
from core.constraint_solver import ConstraintSolver

# Type alias for a closure rule function
# A rule takes two states (pre and post-transition) and returns a boolean indicating validity
ClosureRule = Callable[[QCState, QCState], bool]

# Type alias for a fix suggestion function
# A function that suggests a modification to the target state to satisfy a rule
FixSuggester = Callable[[QCState, QCState], Dict[str, Any]]

class ClosureRuleSet:
    """
    A collection of rules that must hold for any valid state transition.

    This class manages a set of closure rules, provides a mechanism to
    validate a state transition against these rules, and can suggest fixes
    for violations.
    """

    def __init__(self, constraint_solver: ConstraintSolver):
        """
        Initializes the ClosureRuleSet.

        Args:
            constraint_solver: An instance of ConstraintSolver to perform
                               complex validation logic if needed.
        """
        self.rules: Dict[str, ClosureRule] = {}
        self.fix_suggesters: Dict[str, FixSuggester] = {}
        self.constraint_solver = constraint_solver

    def add_rule(self, name: str, rule: ClosureRule, suggester: FixSuggester = None):
        """
        Adds a new closure rule to the set.

        Args:
            name: The name of the rule (e.g., "energy_conservation").
            rule: A callable that implements the rule logic.
            suggester: An optional callable that suggests a fix if the rule is violated.
        """
        if name in self.rules:
            raise ValueError(f"Rule with name '{name}' already exists.")
        self.rules[name] = rule
        if suggester:
            self.fix_suggesters[name] = suggester

    def validate_transition(self, source_state: QCState, target_state: QCState) -> Tuple[bool, List[ConstraintViolation]]:
        """
        Validates a transition between two states against all registered rules.

        Args:
            source_state: The state before the transition.
            target_state: The state after the transition.

        Returns:
            A tuple containing:
            - bool: True if the transition is valid, False otherwise.
            - list: A list of ConstraintViolation objects for any failed rules.
        """
        violations: List[ConstraintViolation] = []
        is_valid = True

        for name, rule in self.rules.items():
            if not rule(source_state, target_state):
                is_valid = False
                violation = ConstraintViolation(
                    constraint_name=name,
                    violation_details={
                        "source_state_id": str(source_state.id),
                        "target_state_id": str(target_state.id),
                        "message": f"Closure rule '{name}' was violated."
                    }
                )
                violations.append(violation)

        return is_valid, violations

    def suggest_fixes(self, source_state: QCState, target_state: QCState, violations: List[ConstraintViolation]) -> Dict[str, Any]:
        """
        Suggests fixes for a list of constraint violations.

        For each violation, if a corresponding fix suggester is available, it
        is called to propose a modification to the target state.

        Args:
            source_state: The source state of the failed transition.
            target_state: The target state of the failed transition.
            violations: A list of violations returned by `validate_transition`.

        Returns:
            A dictionary of suggested modifications for the target state.
        """
        suggested_fixes = {}
        for violation in violations:
            suggester = self.fix_suggesters.get(violation.constraint_name)
            if suggester:
                fix = suggester(source_state, target_state)
                suggested_fixes.update(fix)

        return suggested_fixes

# --- Example Rules and Suggesters ---

def energy_must_not_increase(source: QCState, target: QCState) -> bool:
    """A simple rule: energy should not increase in the final optimization phase."""
    if source.optimization_phase == "exploitation" and target.energy > source.energy:
        return False
    return True

def suggest_lower_energy(source: QCState, target: QCState) -> Dict[str, Any]:
    """Suggests reverting energy to the previous state's level."""
    return {"energy": source.energy}

def lyapunov_potential_must_decrease(source: QCState, target: QCState) -> bool:
    """Rule: Lyapunov potential should strictly decrease or stay the same."""
    return target.lyapunov_potential <= source.lyapunov_potential

def suggest_lower_lyapunov_potential(source: QCState, target: QCState) -> Dict[str, Any]:
    """Suggests reverting lyapunov potential."""
    return {"lyapunov_potential": source.lyapunov_potential}


# Example usage:
if __name__ == '__main__':
    from uuid import uuid4
    from datetime import datetime
    from core.types import SoftwareState, EnergyComponents

    # Dummy states for demonstration
    initial_state = QCState(
        id=uuid4(),
        timestamp=datetime.utcnow(),
        software_state=SoftwareState(component_versions={}, config_hashes={}, status="nominal"),
        energy=100.0,
        energy_components=EnergyComponents(static=50, dynamic=30, interaction=20),
        lyapunov_potential=0.5,
        contraction_factor=0.9,
        optimization_phase="exploitation"
    )

    # A state that violates the energy rule
    invalid_target_state = initial_state.model_copy(update={"energy": 110.0, "id": uuid4()})

    # A state that violates the Lyapunov rule
    invalid_lyapunov_state = initial_state.model_copy(update={"lyapunov_potential": 0.6, "id": uuid4()})

    # A valid state
    valid_target_state = initial_state.model_copy(update={"energy": 90.0, "lyapunov_potential": 0.4, "id": uuid4()})

    # Setup
    solver = ConstraintSolver()
    rule_set = ClosureRuleSet(solver)
    rule_set.add_rule("energy_must_not_increase_in_exploitation", energy_must_not_increase, suggest_lower_energy)
    rule_set.add_rule("lyapunov_potential_must_decrease", lyapunov_potential_must_decrease, suggest_lower_lyapunov_potential)

    # --- Test Case 1: Invalid energy transition ---
    is_valid, violations = rule_set.validate_transition(initial_state, invalid_target_state)
    print(f"Transition 1 Valid: {is_valid}")
    if not is_valid:
        print(f"Violations: {violations}")
        fixes = rule_set.suggest_fixes(initial_state, invalid_target_state, violations)
        print(f"Suggested fixes: {fixes}")

    print("-" * 20)

    # --- Test Case 2: Invalid Lyapunov transition ---
    is_valid_2, violations_2 = rule_set.validate_transition(initial_state, invalid_lyapunov_state)
    print(f"Transition 2 Valid: {is_valid_2}")
    if not is_valid_2:
        print(f"Violations: {violations_2}")
        fixes_2 = rule_set.suggest_fixes(initial_state, invalid_lyapunov_state, violations_2)
        print(f"Suggested fixes: {fixes_2}")

    print("-" * 20)

    # --- Test Case 3: Valid transition ---
    is_valid_3, violations_3 = rule_set.validate_transition(initial_state, valid_target_state)
    print(f"Transition 3 Valid: {is_valid_3}")
    if not is_valid_3:
        print(f"Violations: {violations_3}")
