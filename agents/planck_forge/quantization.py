"""
Energy Quantizer for PlanckForge Agent
"""

from core.types import TaskQuanta

class EnergyQuantizer:
    """
    Assigns discrete energy levels to task quanta.
    """
    def __init__(self, weights: dict | None = None):
        if weights is None:
            self.weights = {
                "description_len": 0.1,
                "verification_criteria_count": 0.5,
                "dependencies_count": 1.0,
                "spec_stub_len": 0.2,
            }
        else:
            self.weights = weights

    def quantize(self, task: TaskQuanta) -> float:
        """
        Calculates the energy of a single task quantum.

        Args:
            task: The task quantum to analyze.

        Returns:
            The calculated energy level.
        """
        energy = 0.0
        energy += len(task.description) * self.weights["description_len"]
        energy += len(task.verification_criteria) * self.weights["verification_criteria_count"]
        energy += len(task.dependencies) * self.weights["dependencies_count"]
        if task.spec_stub:
            energy += len(task.spec_stub) * self.weights["spec_stub_len"]

        return energy

    def quantize_batch(self, tasks: list[TaskQuanta]) -> list[TaskQuanta]:
        """
        Calculates the energy for a batch of task quanta and updates them in place.

        Args:
            tasks: A list of task quanta.

        Returns:
            The list of tasks with their energy levels updated.
        """
        for task in tasks:
            task.energy = self.quantize(task)
        return tasks
