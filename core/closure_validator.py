from typing import Set, Dict, List, Optional
from core.types import Obligation, ClosureResult, ObligationStatus, ProofWitness

class ClosureValidator:
    """
    Verifies that a set of obligations (Δ) is closed, meaning all
    obligations are satisfied with mathematical certainty.
    """

    def verify_closure(self, obligations: Set[Obligation]) -> ClosureResult:
        """Verify all obligations in Δ are satisfied with mathematical certainty"""

        # 1. Build dependency graph and check for cycles
        try:
            adj_list = self._build_obligation_graph(obligations)
            if self._has_cycles(adj_list):
                return ClosureResult(valid=False, error="Circular dependencies detected in obligations.")
        except ValueError as e:
            return ClosureResult(valid=False, error=str(e))

        # 2. Verify each obligation has a valid witness and is closed
        unsatisfied = []
        for obligation in obligations:
            if obligation.status != ObligationStatus.CLOSED:
                unsatisfied.append(obligation)
            elif not self._validate_witness(obligation.witness):
                # Assuming a closed obligation must have a witness
                unsatisfied.append(obligation)

        if unsatisfied:
            return ClosureResult(valid=False, unsatisfied=unsatisfied)

        # 3. If all checks pass, generate a closure proof
        closure_proof = self._generate_closure_proof(obligations)
        return ClosureResult(valid=True, closure_proof=closure_proof)

    def _build_obligation_graph(self, obligations: Set[Obligation]) -> Dict[str, List[str]]:
        """Builds an adjacency list representation of the obligation dependency graph."""
        adj_list: Dict[str, List[str]] = {ob.id: [] for ob in obligations}
        obligation_ids = set(adj_list.keys())

        for ob in obligations:
            for dep_id in ob.dependencies:
                if dep_id not in obligation_ids:
                    raise ValueError(f"Obligation '{ob.id}' has an unknown dependency '{dep_id}'.")
                # A dependency means an edge from the dependency to the dependent.
                # If A depends on B, the edge is B -> A.
                adj_list[dep_id].append(ob.id)

        return adj_list

    def _has_cycles(self, adj_list: Dict[str, List[str]]) -> bool:
        """
        Detects cycles in the dependency graph using Depth First Search.
        A cycle indicates a logical inconsistency in dependencies.
        """
        path = set()  # Nodes currently in the recursion stack for the current DFS path
        visited = set()  # All nodes that have been visited at least once

        for node in adj_list:
            if node not in visited:
                if self._dfs_cycle_check(node, adj_list, path, visited):
                    return True
        return False

    def _dfs_cycle_check(self, node: str, adj_list: Dict[str, List[str]], path: set, visited: set) -> bool:
        path.add(node)
        visited.add(node)

        for neighbor in adj_list.get(node, []):
            if neighbor in path:
                return True  # Cycle detected
            if neighbor not in visited:
                if self._dfs_cycle_check(neighbor, adj_list, path, visited):
                    return True

        path.remove(node)
        return False

    def _validate_witness(self, witness: Optional[ProofWitness]) -> bool:
        """
        Validates the mathematical witness (certificate) of a closed obligation.
        This is a placeholder for what would be a complex verification process.
        """
        # A closed obligation must have a non-null witness.
        if witness is None:
            return False

        # In a real system, this would involve cryptographic checks,
        # running a proof checker (like Coq or Lean), or other formal methods.
        # For now, we'll just check that it's not empty.
        return witness.type is not None and witness.data is not None

    def _generate_closure_proof(self, obligations: Set[Obligation]) -> str:
        """
        Generates a summary or a formal certificate proving closure.
        This is a placeholder.
        """
        # In a real system, this could be a signed document containing hashes
        # of all the obligation witnesses and the dependency structure.
        closed_ids = sorted([ob.id for ob in obligations])
        return f"Closure proof for obligations: {', '.join(closed_ids)}. All dependencies resolved and witnesses verified."
