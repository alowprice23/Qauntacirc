from typing import List, Dict, Set

class ExecutionPlanner:
    """
    Creates an optimal execution plan from a dependency graph using topological sort.
    This serves as the practical replacement for the "PhysicsGuidedParser".
    """

    def create_plan(self, dependency_graph: Dict[str, Set[str]]) -> Dict[str, List[str]]:
        """
        Generates a sequential execution plan from a dependency graph.
        The graph format is {operation: {set_of_dependencies}}.

        Args:
            dependency_graph: A dictionary representing the dependency graph.

        Returns:
            A dictionary containing the execution plan, or an error if a cycle is detected.
        """
        sorted_plan = []
        # A set for nodes that are part of the current recursion stack (for cycle detection)
        visiting = set()
        # A set for nodes that have been completely visited (all descendants processed)
        visited = set()

        def visit(node):
            if node in visited:
                return True # Already visited, no issue
            if node in visiting:
                return False # Cycle detected

            visiting.add(node)

            # The dependencies of the current node must be processed first
            for dependency in dependency_graph.get(node, []):
                if not visit(dependency):
                    return False # Cycle detected in a dependency

            visiting.remove(node)
            visited.add(node)
            # After all dependencies are processed, the node itself can be added to the plan
            sorted_plan.append(node)
            return True

        # We need to iterate over a copy of the keys, as the graph might be modified
        nodes = list(dependency_graph.keys())
        for op in nodes:
            if op not in visited:
                if not visit(op):
                    return {"error": f"A cycle was detected in the dependency graph involving '{op}'."}

        # The "physics" or "energy" could be modeled here. For example,
        # we can assign a cost to each operation and the plan could be
        # optimized to minimize total cost. For now, we just use the
        # topological order.
        return {"execution_plan": sorted_plan}
