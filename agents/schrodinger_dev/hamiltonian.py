import numpy as np

class HamiltonianBuilder:
    def from_specification(self, parsed_spec):
        return np.array([[1.0, 0.0], [0.0, 1.0]])
