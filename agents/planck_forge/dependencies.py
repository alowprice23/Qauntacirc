"""
Dependency Analysis for PlanckForge Agent
"""

from typing import List, Dict, Set
from core.data_models import TaskQuanta

class TaskValidationError(Exception):
    """Custom exception for task validation errors."""
    pass

def validate_dag(tasks: List[TaskQuanta]) -> None:
    """
    Validates that the task dependencies form a Directed Acyclic Graph (DAG).

    Args:
        tasks: A list of task quanta.

    Raises:
        TaskValidationError: If a cycle is detected in the dependency graph.
    """
    adj_list = {task.id: task.dependencies for task in tasks}
    visiting: Set[str] = set()
    visited: Set[str] = set()

    for task_id in adj_list:
        if task_id not in visited:
            if has_cycle_dfs(task_id, adj_list, visiting, visited):
                raise TaskValidationError("A cycle was detected in the task dependencies.")

def has_cycle_dfs(node: str, adj_list: Dict[str, List[str]], visiting: Set[str], visited: Set[str]) -> bool:
    """
    Helper function to detect cycles using Depth First Search.

    Args:
        node: The current node to visit.
        adj_list: The adjacency list of the graph.
        visiting: The set of nodes currently in the recursion stack.
        visited: The set of nodes that have been fully explored.

    Returns:
        True if a cycle is detected, False otherwise.
    """
    visiting.add(node)

    for neighbor in adj_list.get(node, []):
        if neighbor in visiting:
            # Cycle detected
            return True
        if neighbor not in visited:
            if has_cycle_dfs(neighbor, adj_list, visiting, visited):
                return True

    visiting.remove(node)
    visited.add(node)
    return False


def generate_task_dag(tasks: List[TaskQuanta]) -> Dict[str, List[str]]:
    """

    Generates a simple adjacency list representation of the task DAG.
    This function assumes the tasks have already been validated.

    Args:
        tasks: A list of validated task quanta.

    Returns:
        An adjacency list representing the DAG.
    """
    return {task.id: task.dependencies for task in tasks}


def calculate_node_levels(adj_list: Dict[str, List[str]]) -> Dict[str, int]:
    """
    Calculates the level of each node in a DAG.
    The level is the length of the longest path from a source node (level 1).

    Args:
        adj_list: The adjacency list of the DAG.

    Returns:
        A dictionary mapping each node to its level.
    """
    levels: Dict[str, int] = {}

    def get_level(node: str) -> int:
        if node in levels:
            return levels[node]

        if not adj_list.get(node):
            # Node with no dependencies is a source node, level 1
            levels[node] = 1
            return 1

        max_dep_level = 0
        for dep in adj_list[node]:
            max_dep_level = max(max_dep_level, get_level(dep))

        levels[node] = 1 + max_dep_level
        return levels[node]

    for node in adj_list:
        get_level(node)

    return levels
