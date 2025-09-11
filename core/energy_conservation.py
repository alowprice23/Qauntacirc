from typing import List, Dict

class ConservationMonitor:
    """
    Monitors system-wide energy conservation.
    """
    def __init__(self, initial_energy: float):
        self.initial_energy = initial_energy
        self.energy_history: List[float] = [initial_energy]
        self.total_energy_delta = 0.0

    def track_energy_change(self, delta_e: float):
        """
        Tracks an energy change in the system.
        A positive delta_e means energy was added (undesirable).
        A negative delta_e means energy was removed (desirable).
        """
        self.total_energy_delta += delta_e
        new_energy = self.energy_history[-1] + delta_e
        self.energy_history.append(new_energy)

    def is_conserved(self) -> bool:
        """
        Checks if the total energy has been conserved (i.e., not increased).
        This means the total change in energy should be less than or equal to zero.
        """
        return self.total_energy_delta <= 0

    def get_current_energy(self) -> float:
        """Returns the current energy level."""
        return self.energy_history[-1]

    def get_total_delta(self) -> float:
        """Returns the total change in energy since initialization."""
        return self.total_energy_delta
