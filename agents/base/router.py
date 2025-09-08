# agents/base/router.py
"""
The AgentRouter is responsible for routing tasks to the most suitable agent
based on capabilities, performance, and current load.
"""
import heapq
from typing import List, Dict, Any, Tuple, Optional

# Assuming a simple Task definition. In a real system, this would be in core.types
Task = Dict[str, Any]

# Forward-declaration of QuantumAgent to avoid circular import
# In a real scenario, you might use `from __future__ import annotations` (Python 3.7+)
# or a more sophisticated dependency management.
class QuantumAgent:
    pass

class AgentRouter:
    """
    Routes tasks to registered agents based on a scoring model.
    """
    def __init__(self):
        self.agents: List[Dict[str, Any]] = []
        self.task_queue: List[Tuple[int, Task]] = []  # Priority queue: (priority, task)
        self.agent_load: Dict[str, int] = {} # agent_id -> number of active tasks

    def register_agent(self, agent: QuantumAgent, capabilities: List[str], initial_score: float = 1.0):
        """
        Registers an agent with the router.

        Args:
            agent: The agent instance to register.
            capabilities: A list of keywords describing what the agent can do.
            initial_score: An initial performance score for the agent.
        """
        agent_id = agent.agent_id
        if agent_id in self.agent_load:
            print(f"Agent {agent_id} is already registered.")
            return

        self.agents.append({
            "instance": agent,
            "id": agent_id,
            "capabilities": set(capabilities),
            "score": initial_score
        })
        self.agent_load[agent_id] = 0
        print(f"Agent {agent.name} ({agent_id}) registered with capabilities: {capabilities}")

    def enqueue_task(self, task: Task, priority: int = 0):
        """
        Adds a task to the priority queue.

        Args:
            task: The task to be routed.
            priority: The priority of the task (lower number is higher priority).
        """
        heapq.heappush(self.task_queue, (priority, task))

    def _score_agent_for_task(self, agent: Dict[str, Any], task: Task) -> float:
        """
        Calculates a score indicating how suitable an agent is for a given task.
        """
        required_caps = set(task.get("required_capabilities", []))

        # Capability matching score (e.g., Jaccard similarity)
        match_score = len(agent["capabilities"].intersection(required_caps)) / len(agent["capabilities"].union(required_caps))
        if not agent["capabilities"].union(required_caps): # Avoid division by zero
            match_score = 1.0 if not required_caps else 0.0

        # Performance score (from historical data, e.g., success rate)
        perf_score = agent["score"]

        # Load balancing factor (lower load is better)
        load_factor = 1.0 / (1.0 + self.agent_load.get(agent["id"], 0))

        # Combine scores (weights can be tuned)
        final_score = (0.5 * match_score) + (0.3 * perf_score) + (0.2 * load_factor)
        return final_score

    def select_agent_for_task(self, task: Task) -> Optional[QuantumAgent]:
        """
        Selects the best agent for a task from the available pool.
        """
        if not self.agents:
            return None

        best_agent = None
        highest_score = -1.0

        for agent_info in self.agents:
            agent_instance = agent_info["instance"]
            if not agent_instance.is_active:
                continue

            score = self._score_agent_for_task(agent_info, task)
            if score > highest_score:
                highest_score = score
                best_agent = agent_instance

        return best_agent

    def dispatch(self) -> bool:
        """
        Dispatches the highest-priority task from the queue to the best agent.
        """
        if not self.task_queue:
            return False # No tasks to dispatch

        priority, task = heapq.heappop(self.task_queue)

        print(f"Dispatching task (priority {priority}): {task.get('name', 'Unnamed Task')}")

        agent = self.select_agent_for_task(task)

        if agent:
            print(f"Routing task to agent: {agent.name}")
            self.agent_load[agent.agent_id] += 1

            # In a real system, this would be an async call
            # The agent would then report back when it's finished to decrement the load
            try:
                # Assuming the task contains the state needed by the agent's run method
                initial_state = task.get("state")
                agent.run(initial_state)
            finally:
                # This is simplified; in a real async system, a callback would handle this
                self.agent_load[agent.agent_id] -= 1

            return True
        else:
            print("No suitable agent found for the task. Re-queuing.")
            self.enqueue_task(task, priority) # Re-queue if no agent is available
            return False

    def update_agent_score(self, agent_id: str, new_score: float):
        """Updates the performance score of an agent."""
        for agent in self.agents:
            if agent["id"] == agent_id:
                agent["score"] = new_score
                break
