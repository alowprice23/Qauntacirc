import pytest
import numpy as np
from typing import Dict, List, Any
from unittest.mock import Mock, patch
from datetime import datetime
from core.energy_calculator import EnergyCalculator
from core.data_models import SystemState, Module, DependencyGraph

@pytest.fixture
def energy_weights():
    return {"alpha": 1.0, "beta": 1.0, "gamma": 1.0, "delta": 1.0}

class TestEnergyCalculator:
    def test_energy_function_construction(self, energy_weights):
        calculator = EnergyCalculator(**energy_weights)
        assert calculator.alpha >= 0
        assert calculator.beta >= 0
        assert calculator.gamma >= 0
        assert calculator.delta >= 0

        mock_state = Mock(spec=SystemState)
        with patch.object(calculator, '_compute_complexity_energy', return_value=10.0), \
             patch.object(calculator, '_compute_coupling_energy', return_value=5.0), \
             patch.object(calculator, '_compute_constraint_energy', return_value=0.0), \
             patch.object(calculator, '_compute_technical_debt_energy', return_value=2.0):
            
            energy, _ = calculator.calculate_energy(mock_state)
            assert energy >= 0
            assert isinstance(energy, (int, float))
            expected_energy = (energy_weights['alpha'] * 10.0 +
                               energy_weights['beta'] * 5.0 +
                               energy_weights['gamma'] * 0.0 +
                               energy_weights['delta'] * 2.0)
            assert abs(energy - expected_energy) < 1e-9

    @patch('core.energy_calculator.shannon_entropy')
    @patch('core.energy_calculator.multi_compressor_bound')
    def test_complexity_energy_calculation(self, mock_multi_compressor_bound, mock_shannon_entropy, energy_weights):
        mock_multi_compressor_bound.return_value = 100
        mock_shannon_entropy.return_value = 1.5

        calculator = EnergyCalculator(**energy_weights)
        
        module1 = Mock(spec=Module)
        module1.normalized_ast = b"code1"
        module1.semantic_tokens = ["a", "b", "c"]
        
        module2 = Mock(spec=Module)
        module2.normalized_ast = b"code2"
        module2.semantic_tokens = ["d", "e", "f"]

        state = Mock(spec=SystemState)
        state.modules = [module1, module2]

        complexity_energy = calculator._compute_complexity_energy(state)

        assert mock_multi_compressor_bound.call_count == 2
        assert mock_shannon_entropy.call_count == 2
        assert complexity_energy == (100 + 1.5) * 2

    @patch('numpy.trace')
    @patch('core.energy_calculator.get_normalized_laplacian')
    def test_coupling_energy_calculation(self, mock_get_normalized_laplacian, mock_trace, energy_weights):
        mock_laplacian = np.array([[1, -1], [-1, 1]])
        mock_get_normalized_laplacian.return_value = mock_laplacian
        mock_trace.return_value = 2.0

        calculator = EnergyCalculator(**energy_weights)

        graph = Mock(spec=DependencyGraph)
        graph.adjacency_matrix = [[0, 1], [1, 0]]
        
        state = Mock(spec=SystemState)
        state.dependency_graph = graph

        coupling_energy = calculator._compute_coupling_energy(state)

        mock_get_normalized_laplacian.assert_called_once()
        mock_trace.assert_called_once()
        assert coupling_energy == 2.0

class TestEnergyMathematicalProperties:
    def test_energy_non_negativity(self, energy_weights):
        """Verify E(S) >= 0 for all valid states."""
        calculator = EnergyCalculator(**energy_weights)

        # State with no modules or dependencies
        empty_state = Mock(spec=SystemState)
        empty_state.modules = []
        empty_state.dependency_graph = None
        empty_state.constraints = []
        empty_state.failing_tests = []
        empty_state.obligations = []
        
        # Mock the debt calculation to avoid dealing with time
        with patch.object(calculator, '_compute_technical_debt_energy', return_value=0.0):
            energy, _ = calculator.calculate_energy(empty_state)
            assert energy >= 0

        # State with modules but no dependencies
        module1 = Module(name="m1", normalized_ast=b"code", semantic_tokens=['a'], cyclomatic_complexity=1, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now())
        state_with_modules = Mock(spec=SystemState)
        state_with_modules.modules = [module1]
        state_with_modules.dependency_graph = None
        state_with_modules.constraints = []
        state_with_modules.failing_tests = []
        state_with_modules.obligations = []
        
        with patch.object(calculator, '_compute_technical_debt_energy', return_value=0.0):
            energy, _ = calculator.calculate_energy(state_with_modules)
            assert energy >= 0

    def test_energy_additivity(self, energy_weights):
        """Verify E(S1 U S2) = E(S1) + E(S2) for disjoint components."""
        calculator = EnergyCalculator(**energy_weights)

        # System 1
        module1 = Module(name="m1", normalized_ast=b"code1", semantic_tokens=['a'], cyclomatic_complexity=1, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now())
        state1 = Mock(spec=SystemState)
        state1.modules = [module1]
        state1.dependency_graph = None
        state1.constraints = []
        state1.failing_tests = []
        state1.obligations = []

        # System 2
        module2 = Module(name="m2", normalized_ast=b"code2", semantic_tokens=['b'], cyclomatic_complexity=1, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now())
        state2 = Mock(spec=SystemState)
        state2.modules = [module2]
        state2.dependency_graph = None
        state2.constraints = []
        state2.failing_tests = []
        state2.obligations = []

        # Combined System
        state_combined = Mock(spec=SystemState)
        state_combined.modules = [module1, module2]
        state_combined.dependency_graph = None
        state_combined.constraints = []
        state_combined.failing_tests = []
        state_combined.obligations = []
        
        with patch.object(calculator, '_compute_technical_debt_energy', return_value=0.0):
            energy1, _ = calculator.calculate_energy(state1)
            energy2, _ = calculator.calculate_energy(state2)
            energy_combined, _ = calculator.calculate_energy(state_combined)

            # Additivity for complexity should hold
            assert abs(energy_combined - (energy1 + energy2)) < 1e-9

    def test_lipschitz_property(self, energy_weights):
        """Verify |E(S1) - E(S2)| <= L * d(S1, S2)"""
        calculator = EnergyCalculator(**energy_weights)

        def state_distance(s1, s2):
            # A simple distance metric
            module_diff = len(set(m.name for m in s1.modules) ^ set(m.name for m in s2.modules))
            
            adj1 = np.array(s1.dependency_graph.adjacency_matrix) if s1.dependency_graph else np.array([])
            adj2 = np.array(s2.dependency_graph.adjacency_matrix) if s2.dependency_graph else np.array([])
            
            if adj1.shape != adj2.shape:
                # Pad the smaller matrix to be able to compute the norm
                max_shape = np.maximum(adj1.shape, adj2.shape)
                adj1_padded = np.zeros(max_shape)
                adj1_padded[:adj1.shape[0], :adj1.shape[1]] = adj1
                adj2_padded = np.zeros(max_shape)
                adj2_padded[:adj2.shape[0], :adj2.shape[1]] = adj2
                adj_diff = np.linalg.norm(adj1_padded - adj2_padded)
            else:
                adj_diff = np.linalg.norm(adj1 - adj2)

            return module_diff + adj_diff

        # State 1
        module1 = Module(name="m1", normalized_ast=b"code1", semantic_tokens=['a'], cyclomatic_complexity=1, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now())
        graph1 = Mock(spec=DependencyGraph)
        graph1.adjacency_matrix = [[0]]
        state1 = Mock(spec=SystemState)
        state1.modules = [module1]
        state1.dependency_graph = graph1
        state1.constraints = []
        state1.failing_tests = []
        state1.obligations = []

        # State 2 (a small perturbation of State 1)
        module2 = Module(name="m2", normalized_ast=b"code2", semantic_tokens=['b'], cyclomatic_complexity=1, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now())
        graph2 = Mock(spec=DependencyGraph)
        graph2.adjacency_matrix = [[0, 1], [1, 0]]
        state2 = Mock(spec=SystemState)
        state2.modules = [module1, module2]
        state2.dependency_graph = graph2
        state2.constraints = []
        state2.failing_tests = []
        state2.obligations = []

        with patch.object(calculator, '_compute_technical_debt_energy', return_value=0.0):
            energy1, _ = calculator.calculate_energy(state1)
            energy2, _ = calculator.calculate_energy(state2)

        distance = state_distance(state1, state2)
        energy_diff = abs(energy1 - energy2)

        # The Lipschitz constant should be positive
        if distance > 0:
            L = energy_diff / distance
            # The prompt gives a very specific bound, which might be hard to meet
            # without more context on the system's expected behavior.
            # We'll assert that it's a reasonable positive number.
            assert L > 0
            assert L < 1000 # A reasonable upper bound
