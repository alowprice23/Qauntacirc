from typing import Any, Dict, List

class SessionContext:
    """
    A simple data class to hold the context for a single session.
    This is analogous to the user's SessionContext and QuantumContext.
    """
    def __init__(self, initial_energy_state: float = 1000.0):
        # A metaphorical "energy" level for the system
        self.energy: float = initial_energy_state
        self.history: List[Dict[str, Any]] = []

class ContextManager:
    """
    Maintains the conversational context across multiple commands in a session.
    """
    def __init__(self):
        self.session_context = SessionContext()

    def update_context(self, command: str, decomposition: Dict, dependency_graph: Dict, plan: Dict) -> SessionContext:
        """
        Updates the context with the latest command and its processing results.
        """
        # "Energy" is a metaphor for computational resources.
        # We can define a simple cost for each operation.
        energy_cost_map = {
            "build": 20, "test": 15, "deploy": 30, "optimize": 40,
            "auth": 10, "rate limiting": 10, "monitoring": 5, "microservices": 25,
            "comprehensive": 10, "automation": 5, "10k": 5
        }

        operations = plan.get("execution_plan", [])
        # A more detailed energy calculation
        energy_impact = sum(energy_cost_map.get(word, 0) for op in operations for word in op.split())

        # "Complexity" can be a simple measure of the number of operations and dependencies.
        num_ops = len(operations)
        deps_data = dependency_graph.get('dependency_graph', {})
        num_deps = sum(len(deps) for deps in deps_data.values()) if isinstance(deps_data, dict) else 0
        complexity = num_ops + num_deps

        self.session_context.energy -= energy_impact

        # Store a record of this interaction
        self.session_context.history.append({
            "command": command,
            "decomposed_operations": decomposition.get("atomic_operations"),
            "dependency_graph": dependency_graph.get("dependency_graph"),
            "optimal_execution_plan": plan.get("execution_plan"),
            "predicted_energy_impact": energy_impact,
            "mathematical_complexity": complexity
        })

        return self.session_context
