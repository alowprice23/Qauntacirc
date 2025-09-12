import math
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any

from common.base_agent import PhysicsBasedAgent
from common.data_models import (
    WorkloadDistribution, ResourceAllocation, SystemState, Observable, DeploymentPlan
)
from common.utils import BoseEinsteinAllocator

@dataclass
class TaskAllocation:
    """Details of resource allocation for a single task type."""
    task_type: str
    energy_level: float
    occupation_number: float
    replicas: int
    efficiency_score: float

class BoseBoostAgent(PhysicsBasedAgent):
    def __init__(self):
        super().__init__(
            physics_principle="Bose-Einstein Statistics",
            mathematical_formula="n_B = 1/(e^((ε-μ)/kT) - 1)"
        )
        self.k_B = 8.617333e-5  # Boltzmann constant (effective units)
        self.resource_allocator = BoseEinsteinAllocator()

    def apply_physics_principle(self, workload: WorkloadDistribution, temperature: float, **kwargs) -> ResourceAllocation:
        """Allocate resources using Bose-Einstein statistics"""
        if temperature <= 0:
            raise ValueError("Temperature must be positive for Bose-Einstein statistics.")

        energy_levels = self._extract_task_energy_levels(workload)
        μ = self._compute_chemical_potential(workload, energy_levels, temperature)

        allocations: Dict[str, TaskAllocation] = {}
        for task_type, ε in energy_levels.items():
            exponent = (ε - μ) / (self.k_B * temperature)

            # Avoid math domain errors and overflow
            try:
                denominator = math.exp(exponent) - 1.0
            except OverflowError:
                denominator = float('inf')

            if abs(denominator) < 1e-9:
                # This indicates potential for Bose-Einstein condensation; assign max resources
                n_B = float(workload.max_replicas_per_task)
            else:
                n_B = 1.0 / denominator

            # If μ > ε, n_B will be negative, which is unphysical.
            # This implies the chemical potential was computed incorrectly or the model doesn't apply.
            # For robustness, we treat this as a low-energy state that gets a baseline allocation.
            if n_B < 0:
                n_B = 1.0

            n_B = min(n_B, float(workload.max_replicas_per_task))
            n_B = max(n_B, 1.0)  # Ensure at least one replica for every task type

            allocations[task_type] = TaskAllocation(
                task_type=task_type,
                energy_level=ε,
                occupation_number=n_B,
                replicas=int(round(n_B)),
                efficiency_score=n_B / ε if ε > 0 else float('inf')
            )

        deployment_plan = self.resource_allocator.create_deployment_plan(allocations)

        return ResourceAllocation(
            allocations=allocations,
            chemical_potential=μ,
            temperature=temperature,
            deployment_plan=deployment_plan,
            total_efficiency=sum(alloc.efficiency_score for alloc in allocations.values())
        )

    def _extract_task_energy_levels(self, workload: WorkloadDistribution) -> Dict[str, float]:
        """Placeholder to extract energy levels (e.g., complexity) from workload."""
        return {task_type: task_data.get('complexity', 1.0)
                for task_type, task_data in workload.tasks.items()}

    def _compute_chemical_potential(self, workload: WorkloadDistribution, energy_levels: Dict[str, float], temperature: float) -> float:
        """
        Placeholder to compute chemical potential μ.
        μ must be less than all energy levels for the occupation number to be positive.
        A simple mock: set μ to be slightly below the lowest energy level.
        """
        if not energy_levels:
            return 0.0
        min_energy = min(energy_levels.values())
        return min_energy - self.k_B * temperature

    def measure_observable(self, system_state: SystemState) -> Observable:
        """Measure the resource allocation efficiency."""
        # This is a mock measurement, as it depends on a dynamic workload.
        return Observable(
            name="allocation_efficiency",
            value=np.random.uniform(0.8, 0.95),
            unit="efficiency_score"
        )
