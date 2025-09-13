"""
Energy Quantizer for PlanckForge Agent
Implements the E_n = n * h * v model for task energy calculation.
"""

from typing import List, Dict
from core.data_models import TaskQuanta
from .dependencies import calculate_node_levels

class EnergyQuantizer:
    """
    Assigns discrete energy levels to task quanta based on the E_n = nhν model.

    The energy of a task is quantized, determined by its complexity (ν), its
    position in the dependency graph (n), and a fundamental constant (h).
    """
    def __init__(
        self,
        planck_constant: float = 1.0,
        base_frequency_weights: Dict[str, float] | None = None,
    ):
        """
        Initializes the EnergyQuantizer.

        Args:
            planck_constant: The 'h' in the energy formula, a scaling factor.
            base_frequency_weights: Weights to calculate the base frequency (ν) of a task.
        """
        self.planck_constant = planck_constant
        if base_frequency_weights is None:
            self.base_frequency_weights = {
                "description_len": 0.1,
                "verification_criteria_count": 0.5,
                "dependencies_count": 0.2,  # Reduced weight as it's now part of 'n'
                "spec_stub_len": 0.2,
            }
        else:
            self.base_frequency_weights = base_frequency_weights

    def _calculate_base_frequency(self, task: TaskQuanta) -> float:
        """
        Calculates the base frequency (ν) of a single task quantum.
        This represents the intrinsic complexity of the task.

        Args:
            task: The task quantum to analyze.

        Returns:
            The calculated base frequency.
        """
        frequency = 0.0
        frequency += len(task.description) * self.base_frequency_weights["description_len"]
        frequency += len(task.verification_criteria) * self.base_frequency_weights["verification_criteria_count"]
        frequency += len(task.dependencies) * self.base_frequency_weights["dependencies_count"]
        if task.spec_stub:
            frequency += len(task.spec_stub) * self.base_frequency_weights["spec_stub_len"]

        # Ensure frequency is non-zero to avoid energy being zero for n > 0
        return max(frequency, 1e-6)

    def quantize_batch(self, tasks: List[TaskQuanta]) -> List[TaskQuanta]:
        """
        Calculates and assigns quantized energy levels for a batch of tasks.

        This method first constructs a dependency graph to determine the quantum
        level 'n' for each task. It then calculates the base frequency 'ν' for
        each task and combines them using the formula E = n * h * ν.

        Args:
            tasks: A list of task quanta.

        Returns:
            The list of tasks with their 'energy' attribute updated.
        """
        if not tasks:
            return []

        adj_list = {task.id: task.dependencies for task in tasks}
        task_map = {task.id: task for task in tasks}

        # 1. Calculate the quantum level 'n' for each task.
        node_levels = calculate_node_levels(adj_list)

        # 2. Calculate and assign energy and other physics properties for each task.
        for task_id, task in task_map.items():
            n = node_levels.get(task_id, 1)  # Default to level 1 if not in graph
            v = self._calculate_base_frequency(task)
            energy = n * self.planck_constant * v

            task.n = n
            task.frequency = v
            task.energy = energy

        return list(task_map.values())
