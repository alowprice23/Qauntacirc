from typing import List, Callable, Any

from agents.base.contracts import Contract

class ContractComposer:
    """
    Composes agent contracts using Hoare logic.
    """
    @staticmethod
    def sequential_compose(contracts: List[Contract]) -> Contract:
        """
        Composes a list of contracts sequentially.
        {P} F {Q} and {Q} G {R} becomes {P} F;G {R}
        """
        if not contracts:
            raise ValueError("Cannot compose an empty list of contracts.")

        composed_contract = contracts[0]
        for next_contract in contracts[1:]:
            # This is a simplified composition. A real implementation would
            # involve a theorem prover to ensure Q of the first contract
            # implies P of the second.
            if composed_contract.postcondition != next_contract.precondition:
                print(f"Warning: Postcondition of {composed_contract.name} does not match precondition of {next_contract.name}. Composition may be invalid.")

            composed_contract = Contract(
                name=f"{composed_contract.name};{next_contract.name}",
                precondition=composed_contract.precondition,
                postcondition=next_contract.postcondition,
                action=lambda state: next_contract.action(composed_contract.action(state))
            )
        return composed_contract

    @staticmethod
    def parallel_compose(contracts: List[Contract]) -> Contract:
        """
        Composes a list of contracts in parallel.
        {P1} F {Q1} and {P2} G {Q2} becomes {P1 and P2} F||G {Q1 and Q2}
        """
        if not contracts:
            raise ValueError("Cannot compose an empty list of contracts.")

        def combined_precondition(state: Any) -> bool:
            return all(c.precondition(state) for c in contracts)

        def combined_postcondition(state: Any) -> bool:
            return all(c.postcondition(state) for c in contracts)

        def combined_action(state: Any) -> Any:
            # In a real system, this would involve parallel execution.
            # Here, we simulate it sequentially.
            for contract in contracts:
                state = contract.action(state)
            return state

        composed_name = "||".join([c.name for c in contracts])

        return Contract(
            name=composed_name,
            precondition=combined_precondition,
            postcondition=combined_postcondition,
            action=combined_action
        )
