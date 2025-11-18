# agents/planck_forge/ops.py
"""
Operations for the PlanckForge Agent.

This module contains the logic for parsing LLM-generated task specifications,
validating them against a set of closure rules (e.g., ensuring the task
graph is a DAG), and structuring them for downstream consumption.
"""

import json
from typing import List, Dict, Any, Set, Tuple

# A simple type alias for a task
Task = Dict[str, Any]

class TaskValidationError(Exception):
    """Custom exception for task validation errors."""
    pass

def parse_llm_output(llm_output: str) -> List[Task]:
    """
    Parses the JSON output from the LLM into a list of task dictionaries.

    Args:
        llm_output: The raw string output from the LLM.

    Returns:
        A list of task dictionaries.

    Raises:
        TaskValidationError: If the output is not valid JSON or if the structure
                             is incorrect.
    """
    try:
        data = json.loads(llm_output)
        if "tasks" not in data or not isinstance(data["tasks"], list):
            raise TaskValidationError("LLM output is missing a 'tasks' list.")
        return data["tasks"]
    except json.JSONDecodeError:
        raise TaskValidationError("Failed to decode LLM output as JSON.")


def validate_task_set(tasks: List[Task]) -> None:
    """
    Validates a set of tasks against a series of closure rules.

    Args:
        tasks: A list of task dictionaries.

    Raises:
        TaskValidationError: If any validation rule fails.
    """
    if not tasks:
        raise TaskValidationError("Task set cannot be empty.")

    task_ids = {task.get("task_id") for task in tasks}
    if None in task_ids:
        raise TaskValidationError("All tasks must have a 'task_id'.")
    if len(task_ids) != len(tasks):
        raise TaskValidationError("Task IDs must be unique.")

    for task in tasks:
        # Rule: Each task must have a description and verification criteria.
        if not task.get("description") or not task.get("verification_criteria"):
            raise TaskValidationError(f"Task {task['task_id']} is missing description or verification criteria.")

        # Rule: Dependencies must be valid task IDs.
        dependencies = task.get("dependencies", [])
        if not all(dep in task_ids for dep in dependencies):
            raise TaskValidationError(f"Task {task['task_id']} has an invalid dependency.")

    # Rule: The dependency graph must be acyclic.
    validate_dag(tasks)


def validate_dag(tasks: List[Task]) -> None:
    """
    Validates that the task dependencies form a Directed Acyclic Graph (DAG).

    Args:
        tasks: A list of task dictionaries.

    Raises:
        TaskValidationError: If a cycle is detected in the dependency graph.
    """
    adj_list = {task["task_id"]: task.get("dependencies", []) for task in tasks}
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


def generate_task_dag(tasks: List[Task]) -> Dict[str, List[str]]:
    """

    Generates a simple adjacency list representation of the task DAG.
    This function assumes the tasks have already been validated.

    Args:
        tasks: A list of validated task dictionaries.

    Returns:
        An adjacency list representing the DAG.
    """
    return {task["task_id"]: task.get("dependencies", []) for task in tasks}
