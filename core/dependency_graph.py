from typing import Dict, List, Set

class DependencyGraph:
    def __init__(self):
        self.graph: Dict[str, Set[str]] = {}
        self.agent_outputs: Dict[str, Set[str]] = {}

    def add_agent(self, agent_name: str, inputs: List[str], outputs: List[str]):
        if agent_name not in self.graph:
            self.graph[agent_name] = set(inputs)
            self.agent_outputs[agent_name] = set(outputs)

    def resolve_dependencies(self) -> List[str]:
        resolved_order = []
        resolved_outputs = set()

        while len(resolved_order) < len(self.graph):
            unresolved_agents = self.graph.keys() - set(resolved_order)
            made_progress = False

            for agent_name in unresolved_agents:
                if self.graph[agent_name].issubset(resolved_outputs):
                    resolved_order.append(agent_name)
                    resolved_outputs.update(self.agent_outputs[agent_name])
                    made_progress = True

            if not made_progress:
                raise Exception("Circular dependency detected.")

        return resolved_order