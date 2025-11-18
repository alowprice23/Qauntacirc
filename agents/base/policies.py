# agents/base/policies.py
"""
Policy framework for agent action validation, ensuring alignment with
system-wide operational constraints and budgets.
"""

import abc
from typing import List

from core.types import AgentTask as Proposal
from core.error_budget import ErrorBudget


class Policy(abc.ABC):
    """Abstract base class for a policy."""

    @abc.abstractmethod
    def check(self, proposal: Proposal) -> bool:
        """
        Checks if a proposal satisfies the policy.

        Args:
            proposal (Proposal): The proposal to check.

        Returns:
            bool: True if the proposal is compliant, False otherwise.
        """
        pass


class PolicyEngine:
    """
    The PolicyEngine aggregates multiple policies and provides a single
    validation point.
    """
    def __init__(self, policies: List[Policy]):
        self.policies = policies

    def validate(self, proposal: Proposal) -> bool:
        """
        Validates a proposal against all registered policies.

        Args:
            proposal (Proposal): The proposal to validate.

        Returns:
            bool: True if the proposal satisfies all policies, False otherwise.
        """
        return all(policy.check(proposal) for policy in self.policies)


class RigorPolicy(Policy):
    """
    A policy that enforces a minimum rigor level for proposals.
    Rigor might be a measure of confidence, evidence, or required computational proof.
    """
    def __init__(self, required_rigor: float):
        if not (0.0 <= required_rigor <= 1.0):
            raise ValueError("Required rigor must be between 0.0 and 1.0")
        self.required_rigor = required_rigor

    def check(self, proposal: Proposal) -> bool:
        """
        Checks if the proposal's rigor level meets the requirement.
        """
        metadata = proposal.payload.get("metadata", {})
        rigor = metadata.get("rigor", 0.0)
        return rigor >= self.required_rigor


class EnergyBudgetPolicy(Policy):
    """
    A policy that ensures a proposed action does not exceed the allocated
    energy budget.
    """
    def __init__(self, error_budget: ErrorBudget):
        self.error_budget = error_budget

    def check(self, proposal: Proposal) -> bool:
        """
        Checks if the estimated energy cost of the proposal is within the
        available error/energy budget.
        """
        metadata = proposal.payload.get("metadata", {})
        estimated_cost = metadata.get("estimated_energy_cost", 0.0)
        return self.error_budget.is_sufficient(estimated_cost)
