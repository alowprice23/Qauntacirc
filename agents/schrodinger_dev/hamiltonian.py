import numpy as np
from typing import List, Dict, Any
from agents.base import ops as base_ops

def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

class HamiltonianBuilder:
    """
    Constructs the Hamiltonian for a system of code implementations.

    The Hamiltonian models the "energy" of the system, where lower energy
    corresponds to better implementations. The basis states of the system
    are the different code implementations.
    """
    def __init__(self, weights: Dict[str, float]):
        """
        Initializes the HamiltonianBuilder with weights for energy components.

        Args:
            weights: A dictionary of weights for different energy terms, e.g.,
                     {'complexity': 0.5, 'constraints': 1.0, 'similarity': 0.2}
        """
        self.weights = weights

    def _calculate_potential_energy(self, code: str, spec: Dict[str, Any]) -> float:
        """
        Calculates the potential energy (diagonal element) for a single implementation.
        This is the "self-energy" of a code snippet.
        """
        energy = 0.0

        # 1. Energy from cyclomatic complexity
        try:
            ast_tree = base_ops.parse_to_ast(code)
            complexity = base_ops.calculate_cyclomatic_complexity(ast_tree)
            energy += self.weights.get('complexity', 1.0) * complexity
        except SyntaxError:
            # Penalize syntactically incorrect code heavily
            return 1e6

        # 2. Energy from constraint violations (dummy example)
        # A real implementation would parse spec['constraints'] and check them.
        if "performance" in spec.get("constraints", []) and "time.sleep" in code:
            energy += self.weights.get('constraints', 1.0) * 100

        # 3. Energy from code length (as a proxy for simplicity)
        energy += self.weights.get('length', 0.01) * len(code)

        return energy

    def _calculate_interaction_energy(self, code1: str, code2: str) -> float:
        """
        Calculates the interaction energy (off-diagonal element) between two implementations.
        This is based on the similarity of the code snippets.
        """
        if not code1 or not code2:
            return 0.0

        # We use Levenshtein distance as a measure of dissimilarity.
        # A smaller distance means more similarity, thus a stronger (negative) interaction.
        distance = levenshtein_distance(code1, code2)
        max_len = max(len(code1), len(code2))
        normalized_distance = distance / max_len if max_len > 0 else 0

        # The interaction term is negative, encouraging transitions between similar states.
        interaction_energy = -self.weights.get('similarity', 1.0) * (1.0 - normalized_distance)
        return interaction_energy

    def from_specification(
        self,
        implementations: List[str],
        parsed_spec: Dict[str, Any]
    ) -> np.ndarray:
        """
        Builds the Hamiltonian matrix from a specification and a list of implementations.

        Args:
            implementations: A list of code strings, each representing a basis state.
            parsed_spec: A dictionary representing the parsed task specification.

        Returns:
            A numpy array representing the Hamiltonian matrix.
        """
        n_states = len(implementations)
        if n_states == 0:
            return np.array([[]])

        hamiltonian = np.zeros((n_states, n_states))

        # Calculate diagonal elements (potential energy)
        for i in range(n_states):
            hamiltonian[i, i] = self._calculate_potential_energy(implementations[i], parsed_spec)

        # Calculate off-diagonal elements (interaction energy)
        for i in range(n_states):
            for j in range(i + 1, n_states):
                interaction = self._calculate_interaction_energy(implementations[i], implementations[j])
                hamiltonian[i, j] = interaction
                hamiltonian[j, i] = interaction  # Hamiltonian is Hermitian

        return hamiltonian
