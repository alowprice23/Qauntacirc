"""
Operations for the PlanckForge Agent.

This module contains the logic for parsing LLM-generated task specifications,
validating them against a set of closure rules (e.g., ensuring the task
graph is a DAG), and structuring them for downstream consumption.
"""

import json
from typing import List, Dict, Any

from core.data_models import TaskQuanta
from .quantization import EnergyQuantizer
from . import dependencies

class TaskValidationError(Exception):
    """Custom exception for task validation errors."""
    pass

def generate_spec_stub(task: TaskQuanta) -> str:
    """Generates a formal specification stub for a task."""
    stub = f"(* Task: {task.id} - {task.description} *)\n"
    stub += f"Theorem {task.id}_correct : forall (s1 s2 : State),\n"
    stub += f"  implements_{task.id} s1 s2 ->\n"
    for i, criterion in enumerate(task.verification_criteria):
        stub += f"  (* {i+1}. {criterion} *)\n"
        stub += f"  verifies_{i+1} s1 s2 /\\\n"
    stub += "  True.\n"
    return stub

def parse_llm_output(llm_output: str) -> List[TaskQuanta]:
    """
    Parses the JSON output from the LLM into a list of TaskQuanta objects.

    Args:
        llm_output: The raw string output from the LLM.

    Returns:
        A list of task quanta.

    Raises:
        TaskValidationError: If the output is not valid JSON or if the structure
                             is incorrect.
    """
    try:
        data = json.loads(llm_output)
        if "tasks" not in data or not isinstance(data["tasks"], list):
            raise TaskValidationError("LLM output is missing a 'tasks' list.")

        tasks_data = data["tasks"]
        quantas = [TaskQuanta(**task_data) for task_data in tasks_data]

        for quanta in quantas:
            quanta.spec_stub = generate_spec_stub(quanta)

        quantizer = EnergyQuantizer()
        quantas = quantizer.quantize_batch(quantas)

        return quantas

    except json.JSONDecodeError:
        raise TaskValidationError("Failed to decode LLM output as JSON.")
    except Exception as e:
        raise TaskValidationError(f"Failed to parse tasks from LLM output: {e}")


def validate_task_set(tasks: List[TaskQuanta]) -> None:
    """
    Validates a set of tasks against a series of closure rules.

    Args:
        tasks: A list of task quanta.

    Raises:
        TaskValidationError: If any validation rule fails.
    """
    if not tasks:
        raise TaskValidationError("Task set cannot be empty.")

    task_ids = {task.id for task in tasks}
    if len(task_ids) != len(tasks):
        raise TaskValidationError("Task IDs must be unique.")

    for task in tasks:
        # Rule: Each task must have a description and verification criteria.
        if not task.description or not task.verification_criteria:
            raise TaskValidationError(f"Task {task.id} is missing description or verification criteria.")

        # Rule: Dependencies must be valid task IDs.
        if not all(dep in task_ids for dep in task.dependencies):
            raise TaskValidationError(f"Task {task.id} has an invalid dependency.")

    # Rule: The dependency graph must be acyclic.
    dependencies.validate_dag(tasks)

def generate_task_dag(tasks: List[TaskQuanta]) -> Dict[str, List[str]]:
    """
    Generates a simple adjacency list representation of the task DAG.
    This function assumes the tasks have already been validated.

    Args:
        tasks: A list of validated task quanta.

    Returns:
        An adjacency list representing the DAG.
    """
    return dependencies.generate_task_dag(tasks)
