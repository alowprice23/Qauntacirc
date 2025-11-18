# core/error_budget.py

"""
Manages the computational error budget for the system.

In any complex simulation, errors can accumulate from various sources, such as
numerical precision, model simplifications, and stochastic processes. This
module provides a framework for tracking and managing this error budget.
"""

from __future__ import annotations

from typing import Dict, Optional
from uuid import UUID, uuid4
import logging

class ErrorBudget:
    """
    Tracks the consumption of the computational error budget.

    The total budget is composed of different components, each corresponding to a
    potential source of error in the simulation. The orchestrator or other
    components can 'spend' from this budget when they perform operations that
    introduce uncertainty or error.
    """

    def __init__(self, initial_budgets: Dict[str, float]):
        """
        Initializes the ErrorBudget.

        Args:
            initial_budgets: A dictionary mapping error sources (e.g., 'numerical',
                             'sampling', 'model') to their initial budget values.
        """
        if not initial_budgets:
            raise ValueError("Initial budgets cannot be empty.")

        self.budgets: Dict[str, float] = initial_budgets.copy()
        self.initial_budgets: Dict[str, float] = initial_budgets.copy()
        self.log: list[Dict] = []
        logging.info(f"ErrorBudget initialized with: {self.budgets}")

    def spend(self, source: str, amount: float, transaction_id: Optional[UUID] = None):
        """
        Spends a certain amount from a specific error budget source.

        Args:
            source: The error source to spend from (e.g., 'numerical').
            amount: The amount of budget to spend.
            transaction_id: An optional unique ID for this transaction.

        Raises:
            ValueError: If the source does not exist or if the amount is negative.
            RuntimeError: If the budget for the source is depleted.
        """
        if source not in self.budgets:
            raise ValueError(f"Error source '{source}' not found in budget.")
        if amount < 0:
            raise ValueError("Cannot spend a negative amount.")

        if self.budgets[source] < amount:
            logging.error(f"Error budget for '{source}' depleted. Requested: {amount}, Remaining: {self.budgets[source]}")
            raise RuntimeError(f"Error budget for '{source}' depleted.")

        self.budgets[source] -= amount

        log_entry = {
            "transaction_id": transaction_id or uuid4(),
            "source": source,
            "spent": amount,
            "remaining": self.budgets[source]
        }
        self.log.append(log_entry)
        logging.debug(f"Spent {amount} from '{source}' budget. Remaining: {self.budgets[source]}")

    def get_remaining_budget(self, source: str) -> float:
        """
        Gets the remaining budget for a specific source.

        Args:
            source: The name of the error source.

        Returns:
            The remaining budget amount.
        """
        if source not in self.budgets:
            raise ValueError(f"Error source '{source}' not found.")
        return self.budgets[source]

    def get_total_remaining_budget(self) -> float:
        """
        Calculates the total remaining budget across all sources.

        Returns:
            The sum of all remaining budgets.
        """
        return sum(self.budgets.values())

    def get_budget_status(self) -> Dict[str, Dict[str, float]]:
        """
        Provides a summary of the current state of all budget components.

        Returns:
            A dictionary with the status of each budget source, including initial,
            spent, and remaining amounts.
        """
        status = {}
        for source, initial_amount in self.initial_budgets.items():
            remaining = self.budgets[source]
            spent = initial_amount - remaining
            status[source] = {
                "initial": initial_amount,
                "spent": spent,
                "remaining": remaining
            }
        return status

    def reset(self):
        """
        Resets all budgets to their initial values and clears the log.
        """
        self.budgets = self.initial_budgets.copy()
        self.log.clear()
        logging.info("ErrorBudget has been reset to initial state.")

# Example Usage
if __name__ == '__main__':
    initial_budgets = {
        'numerical_precision': 0.1,
        'model_approximation': 0.5,
        'stochastic_sampling': 1.0
    }

    budget_manager = ErrorBudget(initial_budgets)

    print("Initial Budget Status:")
    print(budget_manager.get_budget_status())

    try:
        print("\nSpending 0.2 from 'stochastic_sampling'...")
        budget_manager.spend('stochastic_sampling', 0.2)

        print("Spending 0.05 from 'numerical_precision'...")
        budget_manager.spend('numerical_precision', 0.05)

        print("\nUpdated Budget Status:")
        print(budget_manager.get_budget_status())

        print(f"\nTotal remaining budget: {budget_manager.get_total_remaining_budget():.2f}")

        print("\nTrying to spend more than available...")
        budget_manager.spend('model_approximation', 0.6) # This will raise an error

    except (ValueError, RuntimeError) as e:
        print(f"Caught expected error: {e}")

    print("\nResetting budget...")
    budget_manager.reset()
    print("Budget Status after reset:")
    print(budget_manager.get_budget_status())
