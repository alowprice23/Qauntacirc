from typing import List, Dict, Set

class DependencyAnalyzer:
    """
    Analyzes dependencies between atomic operations using a predefined dependency mapping.
    """

    def __init__(self, dependency_map: Dict[str, List[str]] = None):
        if dependency_map is None:
            # Defines which operation depends on which other operations.
            # e.g., "deploy" depends on "build" and "test".
            self.dependency_map = {
                "deploy": ["build", "test"],
                "deployment automation": ["build", "test"],
                "test": ["build"],
                "generate comprehensive tests": ["build microservices"],
                "optimize": ["test"],
                "optimize for 10k RPS": ["test"],
                "auth": ["build microservices"],
                "rate limiting": ["build microservices"],
                "monitoring": ["deploy"]
            }
        else:
            self.dependency_map = dependency_map

    def analyze_dependencies(self, operations: List[str]) -> Dict[str, Set[str]]:
        """
        Builds a dependency graph for the given list of operations.

        Args:
            operations: A list of atomic operations.

        Returns:
            A dictionary representing the dependency graph (adjacency list).
            Keys are operations, values are a set of operations they depend on.
        """
        dependency_graph = {op: set() for op in operations}

        # To handle synonyms or related keywords, we can map them.
        # e.g., 'build microservices' implies 'build'
        synonym_map = {
            "build microservices": "build",
            "generate comprehensive tests": "test",
            "deployment automation": "deploy",
            "optimize for 10k RPS": "optimize"
        }

        # Create a set of core operations present in the command
        present_ops = set(operations)
        for op in operations:
            if op in synonym_map:
                present_ops.add(synonym_map[op])

        for op in operations:
            # Check for dependencies in the map
            op_key = synonym_map.get(op, op)
            if op_key in self.dependency_map:
                for dep in self.dependency_map[op_key]:
                    # If the dependency is also in the list of operations, add the edge.
                    # We need to check for original keywords and their synonyms.
                    found_dep = False
                    # Find the actual operation string from the input list that matches the dependency
                    for potential_dep_op in operations:
                        if dep == potential_dep_op or dep == synonym_map.get(potential_dep_op):
                           dependency_graph[op].add(potential_dep_op)
                           found_dep = True
                           break

        return {"dependency_graph": dependency_graph}
