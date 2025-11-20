import numpy as np
import math

class TemperatureSchedule:
    """
    Implements quantum-mechanical temperature schedules for annealing.

    Provides adaptive temperature scheduling for exploration and exploitation phases,
    balancing global search with local refinement.
    """
    def __init__(self, initial_temp=1000, final_temp=0.1, steps=10000, schedule_type='exponential'):
        self.initial_temp = initial_temp
        self.final_temp = final_temp
        self.steps = steps
        self.schedule_type = schedule_type
        if schedule_type == 'exponential':
            self.alpha = (final_temp / initial_temp) ** (1.0 / steps)
        elif schedule_type == 'logarithmic':
<<<<<<< HEAD
<<<<<<< HEAD
            # Per README, T_k = c / log(k + 2).
            # To have get_temperature(0) == initial_temp, we need c = initial_temp * log(2).
            self.c = initial_temp * math.log(2)
=======
            self.c = initial_temp / math.log(1 + 1)
>>>>>>> remotes/origin/feat/core-infrastructure
=======
            self.c = initial_temp / math.log(1 + 1)
>>>>>>> remotes/origin/feat/core-infrastructure
        elif schedule_type == 'linear':
            self.beta = (initial_temp - final_temp) / steps

    def get_temperature(self, step):
        """Returns the temperature at a given step."""
        if self.schedule_type == 'exponential':
            return self.initial_temp * (self.alpha ** step)
        elif self.schedule_type == 'logarithmic':
<<<<<<< HEAD
<<<<<<< HEAD
            # Per README, T_k = c / log(k + 2)
            if step < 0:
                return float('inf')
            return self.c / math.log(step + 2)
=======
            return self.c / math.log(1 + step + 1)
>>>>>>> remotes/origin/feat/core-infrastructure
=======
            return self.c / math.log(1 + step + 1)
>>>>>>> remotes/origin/feat/core-infrastructure
        elif self.schedule_type == 'linear':
            return self.initial_temp - self.beta * step
        else:
            raise ValueError(f"Unknown schedule type: {self.schedule_type}")

<<<<<<< HEAD
<<<<<<< HEAD

class GeometricCoolingSchedule:
    """
    A simple container for geometric cooling schedule parameters.
    This class was added to resolve an ImportError in the tests.
    """
    def __init__(self, initial_temp: float, cooling_rate: float, min_temp: float):
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp


=======
>>>>>>> remotes/origin/feat/core-infrastructure
=======
>>>>>>> remotes/origin/feat/core-infrastructure
class TwoPhaseAnnealer:
    """
    A two-phase simulated annealer with quantum-mechanical temperature schedules.

    This annealer uses adaptive temperature scheduling to first explore the
    solution space broadly (exploration phase) and then fine-tune the solution
    in a specific region (exploitation phase). It incorporates Metropolis
    acceptance criteria with quantum tunneling corrections.
    """
    def __init__(self, energy_function, initial_state, schedule: TemperatureSchedule):
        self.energy_function = energy_function
        self.current_state = initial_state
        self.current_energy = self.energy_function(initial_state)
        self.best_state = np.copy(initial_state)
        self.best_energy = self.current_energy
        self.schedule = schedule
        self.history = []

    def _propose_new_state(self, state):
        """Proposes a new state by adding a small random perturbation."""
        # This should be adapted to the specific problem's state representation
        return state + np.random.normal(0, 0.1, size=state.shape)

    def _acceptance_probability(self, old_energy, new_energy, temp):
        """Calculates the Metropolis acceptance probability with a quantum correction term."""
        if new_energy < old_energy:
            return 1.0
        # Quantum tunneling correction (simplified)
        tunneling_factor = np.exp(-(new_energy - old_energy) / temp)
        return tunneling_factor

    def _detect_phase_transition(self, energy_history, window=100):
        """Detects a phase transition based on the variance of recent energy values."""
        if len(energy_history) < window:
            return False
        variance = np.var(energy_history[-window:])
        # Heuristic threshold for phase transition
        return variance > 1.0

    def anneal(self):
        """Performs the two-phase annealing process."""
        # Phase 1: Exploration
        for step in range(self.schedule.steps // 2):
            temp = self.schedule.get_temperature(step)
            new_state = self._propose_new_state(self.current_state)
            new_energy = self.energy_function(new_state)

            if self._acceptance_probability(self.current_energy, new_energy, temp) > np.random.rand():
                self.current_state = new_state
                self.current_energy = new_energy

            if new_energy < self.best_energy:
                self.best_state = np.copy(new_state)
                self.best_energy = new_energy

            self.history.append(self.current_energy)

        # Phase 2: Exploitation (starts from the best state found so far)
        self.current_state = self.best_state
        self.current_energy = self.best_energy

        exploitation_schedule = TemperatureSchedule(
            initial_temp=self.schedule.get_temperature(self.schedule.steps // 2),
            final_temp=self.schedule.final_temp,
            steps=self.schedule.steps // 2,
            schedule_type='exponential'
        )

        for step in range(exploitation_schedule.steps):
            temp = exploitation_schedule.get_temperature(step)
            if temp <= 0: continue

            new_state = self._propose_new_state(self.current_state)
            new_energy = self.energy_function(new_state)

            if self._acceptance_probability(self.current_energy, new_energy, temp) > np.random.rand():
                self.current_state = new_state
                self.current_energy = new_energy

            if new_energy < self.best_energy:
                self.best_state = np.copy(new_state)
                self.best_energy = new_energy

            self.history.append(self.current_energy)

            # Phase transition detection can be used to adapt the schedule dynamically
            if self._detect_phase_transition([e for e in self.history if e is not None]):
                pass # Potentially adjust schedule

        return self.best_state, self.best_energy
