"""
Closure rules for the system.
"""
from core.types import QCState as State, AgentResult as Action

class ClosureRule:
    """
    A base class for closure rules.
    """
    def is_satisfied(self, state: State, action: Action) -> bool:
        """
        Checks if the closure rule is satisfied.
        """
        return True

class ClosureRuleSet:
    """
    A set of closure rules.
    """
    def __init__(self, rules: list[ClosureRule]):
        self.rules = rules

    def is_satisfied(self, state: State, action: Action) -> bool:
        """
        Checks if all closure rules in the set are satisfied.
        """
        return all(rule.is_satisfied(state, action) for rule in self.rules)
