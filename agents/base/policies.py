from typing import List
from core.types import AgentTask as Proposal

class Policy:
    def check(self, proposal: Proposal) -> bool:
        raise NotImplementedError

class PolicyEngine:
    def __init__(self, policies: List[Policy]):
        self.policies = policies

    def validate(self, proposal: Proposal) -> bool:
        return all(policy.check(proposal) for policy in self.policies)

class RigorPolicy(Policy):
    def __init__(self, required_rigor: float):
        self.required_rigor = required_rigor

    def check(self, proposal: Proposal) -> bool:
        return proposal.payload.get("metadata", {}).get("rigor", 0.0) >= self.required_rigor

class EnergyBudgetPolicy(Policy):
    def __init__(self, error_budget):
        self.error_budget = error_budget

    def check(self, proposal: Proposal) -> bool:
        estimated_cost = proposal.payload.get("metadata", {}).get("estimated_energy_cost", 0.0)
        return self.error_budget.is_sufficient(estimated_cost)
