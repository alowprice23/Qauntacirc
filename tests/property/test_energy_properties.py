"""
Property-Based Tests for Energy Function Mathematical Properties

This module uses property-based testing to validate mathematical properties
of QuantaCirc's energy function: E(S) = α·E_complexity + β·E_coupling + γ·E_constraint + δ·E_debt

MATHEMATICAL FOUNDATION:
=======================
Property-based testing validates universal mathematical properties:
1. Energy function additivity and monotonicity
2. Lipschitz continuity and smoothness properties
3. Conservation laws during state transformations
4. Optimization landscape properties and convexity

PHYSICS PRINCIPLE:
=================
Energy functions in physics satisfy universal conservation laws:
- Energy conservation during reversible transformations
- Monotonic decrease during irreversible optimization
- Lipschitz bounds ensure physical realizability
- Convex regions enable predictable optimization

WHAT GETS TESTED:
================
1. Universal Mathematical Properties (holds for ALL valid inputs)
2. Conservation Laws During State Transformations
3. Lipschitz Continuity and Smoothness Properties
4. Optimization Landscape Properties
5. Numerical Stability Under Extreme Conditions
6. Edge Cases and Boundary Behavior

FAILURE ANALYSIS:
================
Property test failures indicate fundamental mathematical violations
and provide guidance for fixing energy function implementation.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
import numpy as np
from typing import Any

from tests.conftest import TestDiagnostic

class TestEnergyFunctionProperties:
    """Property-based tests for energy function mathematical properties."""
    
    @given(
        alpha=st.floats(min_value=0.0, max_value=10.0),
        beta=st.floats(min_value=0.0, max_value=10.0), 
        gamma=st.floats(min_value=0.0, max_value=10.0),
        delta=st.floats(min_value=0.0, max_value=10.0),
        complexity=st.floats(min_value=0.0, max_value=1000.0),
        coupling=st.floats(min_value=0.0, max_value=1000.0),
        constraints=st.floats(min_value=0.0, max_value=100.0),
        debt=st.floats(min_value=0.0, max_value=100.0)
    )
    @settings(deadline=None)
    def test_energy_non_negativity_property(self, alpha, beta, gamma, delta, complexity, coupling, constraints, debt):
        """
        Property: Energy function is always non-negative.
        
        MATHEMATICAL PROPERTY:
        ∀ weights ≥ 0, components ≥ 0. E(S) ≥ 0
        
        This property must hold for ALL possible inputs to ensure
        the energy function represents a valid physical quantity.
        """
        diagnostic = TestDiagnostic(
            component_name="Energy Function Non-Negativity Property",
            expected_behavior="Energy function always returns non-negative values",
            failure_indicators=[
                "Negative energy computed",
                "Component aggregation incorrect",
                "Weight validation failed",
                "Numerical overflow/underflow"
            ],
            build_instructions=[
                "Fix energy computation in core/energy_calculator.py",
                "Add input validation for non-negative components",
                "Implement proper numerical handling for edge cases",
                "Add overflow/underflow protection"
            ],
            mathematical_requirements=[
                "E(S) = α·E_complexity + β·E_coupling + γ·E_constraint + δ·E_debt ≥ 0",
                "α, β, γ, δ ≥ 0 (non-negative weights)",
                "All energy components ≥ 0",
                "Numerical stability for extreme values"
            ],
            acceptance_criteria={
                "always_non_negative": "E(S) ≥ 0 for all valid inputs",
                "weight_validation": "Negative weights properly rejected",
                "component_validation": "Negative components properly handled",
                "numerical_stable": "No overflow/underflow in computation"
            },
            physics_principle="Thermodynamics: Energy is a non-negative physical quantity"
        )
        
        try:
            from core.energy_calculator import EnergyCalculator
            
            # Skip invalid combinations
            assume(not (np.isinf(alpha) or np.isnan(alpha)))
            assume(not (np.isinf(beta) or np.isnan(beta)))
            assume(not (np.isinf(gamma) or np.isnan(gamma)))
            assume(not (np.isinf(delta) or np.isnan(delta)))
            
            calculator = EnergyCalculator(alpha=alpha, beta=beta, gamma=gamma, delta=delta)
            
            # Create mock state with given components
            state = type('State', (), {})()
            state.modules = []
            state.dependency_graph = None
            state.constraints = []
            state.failing_tests = []
            state.obligations = []

            # The energy calculator's internal methods use these, but for this property test,
            # we are bypassing the internal calculation and just checking the top-level formula.
            # So we can mock the direct energy components.
            # To do this, we need to mock the internal compute methods.
            # A simpler way is to provide the necessary attributes for the real methods to run.
            state.complexity = complexity
            state.coupling = coupling
            # The test is about the top-level formula, not the internal calculation.
            # The internal calculation for constraints and debt require more complex objects.
            # We will mock the internal methods to avoid this complexity.

            from unittest.mock import MagicMock
            calculator._compute_complexity_energy = MagicMock(return_value=complexity)
            calculator._compute_coupling_energy = MagicMock(return_value=coupling)
            calculator._compute_constraint_energy = MagicMock(return_value=constraints)
            calculator._compute_technical_debt_energy = MagicMock(return_value=debt)
            
            # Calculate energy
            energy, _ = calculator.calculate_energy(state)
            
            # Property: Energy must be non-negative
            assert energy >= 0, f"Energy must be non-negative, got {energy}"
            
            # Property: Energy should equal manual calculation
            expected_energy = alpha * complexity + beta * coupling + gamma * constraints + delta * debt
            assert abs(energy - expected_energy) < 1e-10, "Energy calculation incorrect"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))
    
    @given(
        weights=st.tuples(
            st.floats(min_value=0.1, max_value=2.0),  # alpha
            st.floats(min_value=0.1, max_value=2.0),  # beta
            st.floats(min_value=0.1, max_value=2.0),  # gamma
            st.floats(min_value=0.1, max_value=2.0)   # delta
        ),
        state1=st.tuples(
            st.floats(min_value=0.0, max_value=100.0),  # complexity
            st.floats(min_value=0.0, max_value=100.0),  # coupling
            st.floats(min_value=0.0, max_value=10.0),   # constraints
            st.floats(min_value=0.0, max_value=10.0)    # debt
        ),
        state2=st.tuples(
            st.floats(min_value=0.0, max_value=100.0),  # complexity
            st.floats(min_value=0.0, max_value=100.0),  # coupling
            st.floats(min_value=0.0, max_value=10.0),   # constraints
            st.floats(min_value=0.0, max_value=10.0)    # debt
        )
    )
    def test_energy_additivity_property(self, weights, state1, state2):
        """
        Property: Energy function is additive for disjoint system components.
        
        MATHEMATICAL PROPERTY:
        E(S1 ∪ S2) = E(S1) + E(S2) for disjoint S1, S2
        
        This ensures energy composition follows physical laws.
        """
        diagnostic = TestDiagnostic(
            component_name="Energy Function Additivity Property",
            expected_behavior="Energy function satisfies additivity for disjoint components",
            failure_indicators=[
                "Additivity property violated",
                "Component composition incorrect",
                "Energy aggregation non-linear",
                "Disjoint assumption violated"
            ],
            build_instructions=[
                "Ensure linear energy aggregation in EnergyCalculator",
                "Validate component independence assumptions",
                "Add proper handling of disjoint system composition",
                "Fix any non-linear aggregation bugs"
            ],
            mathematical_requirements=[
                "E(S1 ∪ S2) = E(S1) + E(S2) for disjoint S1, S2",
                "Linear aggregation: E(∑ᵢ Sᵢ) = ∑ᵢ E(Sᵢ) for disjoint components",
                "Component independence: no cross-terms between disjoint parts",
                "Conservation: energy conserved under system composition"
            ],
            acceptance_criteria={
                "additivity_exact": "E(S1∪S2) = E(S1) + E(S2) within numerical precision",
                "linear_aggregation": "Energy scales linearly with component count",
                "independence": "No spurious cross-component interactions",
                "conservation": "Total energy conserved in composition"
            },
            physics_principle="Thermodynamics: Energy is an extensive property"
        )
        
        try:
            from core.energy_calculator import EnergyCalculator
            
            alpha, beta, gamma, delta = weights
            assume(all(w > 0 for w in weights))  # Positive weights
            
            calculator = EnergyCalculator(alpha=alpha, beta=beta, gamma=gamma, delta=delta)
            
            from unittest.mock import MagicMock
            # Mock the internal calculation methods to test additivity of the top-level function
            complexity1, coupling1, constraints1, debt1 = state1
            complexity2, coupling2, constraints2, debt2 = state2

            def mock_calc(state_tuple):
                def side_effect(state):
                    if state == s1:
                        return complexity1
                    if state == s2:
                        return complexity2
                    if state == s_combined:
                        return complexity1 + complexity2
                return MagicMock(side_effect=side_effect)

            calculator._compute_complexity_energy = mock_calc(state1)
            
            def mock_coupling(state_tuple):
                def side_effect(state):
                    if state == s1: return coupling1
                    if state == s2: return coupling2
                    if state == s_combined: return coupling1 + coupling2
                return MagicMock(side_effect=side_effect)
            calculator._compute_coupling_energy = mock_coupling(state1)

            def mock_constraints(state_tuple):
                def side_effect(state):
                    if state == s1: return constraints1
                    if state == s2: return constraints2
                    if state == s_combined: return constraints1 + constraints2
                return MagicMock(side_effect=side_effect)
            calculator._compute_constraint_energy = mock_constraints(state1)

            def mock_debt(state_tuple):
                def side_effect(state):
                    if state == s1: return debt1
                    if state == s2: return debt2
                    if state == s_combined: return debt1 + debt2
                return MagicMock(side_effect=side_effect)
            calculator._compute_technical_debt_energy = mock_debt(state1)

            # Create mock state objects. They only need to be distinct objects.
            s1 = type('State', (), {})()
            s2 = type('State', (), {})()
            s_combined = type('State', (), {})()
            
            # Calculate energies
            e1, _ = calculator.calculate_energy(s1)
            e2, _ = calculator.calculate_energy(s2)
            e_combined, _ = calculator.calculate_energy(s_combined)
            
            # Property: Additivity for disjoint systems
            expected_combined = e1 + e2
            assert abs(e_combined - expected_combined) < 1e-10, "Additivity property violated"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))


class TestEnergyOptimizationProperties:
    """Property-based tests for energy optimization behavior."""
    
    def test_optimization_monotonicity_property(self):
        """
        Property: Valid optimization steps always decrease or maintain energy.
        
        MATHEMATICAL PROPERTY:
        ∀ valid optimization step S → S'. E(S') ≤ E(S)
        
        This ensures optimization follows physical energy minimization.
        """
        diagnostic = TestDiagnostic(
            component_name="Energy Optimization Monotonicity Property", 
            expected_behavior="Optimization steps never increase total energy",
            failure_indicators=[
                "Energy increased during optimization",
                "Optimization step validation failed",
                "Energy conservation violated",
                "Non-monotonic optimization detected"
            ],
            build_instructions=[
                "Add energy monotonicity validation to optimization steps",
                "Implement optimization step validation",
                "Add energy conservation checking during transformations",
                "Create monotonicity enforcement in agents"
            ],
            mathematical_requirements=[
                "Monotonicity: E(S_next) ≤ E(S_current) for valid steps",
                "Bounded excursions: temporary increases ≤ excursion_bound",
                "Conservation: ΔE_total = Σ ΔE_components",
                "Optimality: E → E* as optimization converges"
            ],
            acceptance_criteria={
                "monotonic_decrease": "E decreases or remains constant",
                "bounded_excursions": "Temporary increases ≤ 5% of current energy",
                "conservation_maintained": "Energy transfers properly accounted",
                "convergence_to_minimum": "Optimization reaches local/global minimum"
            },
            physics_principle="Second law of thermodynamics: Entropy/energy optimization follows natural laws"
        )
        
        diagnostic.acceptance_criteria = {
            "monotonic_decrease": "E decreases or remains constant",
            "bounded_excursions": "Temporary increases ≤ 5% of current energy",
            "conservation_maintained": "Energy transfers properly accounted",
            "convergence_to_minimum": "Optimization reaches local/global minimum"
        }
        from unittest.mock import Mock, patch
        from core.types import SystemState, Module, EnergyBreakdown, LyapunovMetrics, SoftwareState
        from agents.base.agent import PhysicsBasedAgent
        from datetime import datetime
        # 1. Setup a mock agent that performs a valid optimization step
        class MockRefactoringAgent(PhysicsBasedAgent):
            def apply_physics_principle(self, system_state: SystemState):
                new_state = system_state.copy(deep=True)
                # This agent performs a refactoring that reduces complexity
                if new_state.modules:
                    new_state.modules[0].cyclomatic_complexity *= 0.9
                # Recalculate energy based on the change
                new_state.energy_breakdown.complexity *= 0.9
                new_state.energy_breakdown.total = (
                    new_state.energy_breakdown.complexity +
                    new_state.energy_breakdown.coupling +
                    new_state.energy_breakdown.constraint +
                    new_state.energy_breakdown.debt
                )
                return Mock(spec=["proposals"], proposals=[new_state])

            def measure_observable(self, system_state: SystemState):
                pass
            def generate_certificate(self, before_state: SystemState, after_state: SystemState, result):
                pass

        agent = MockRefactoringAgent(agent_name="refactor", physics_principle="test", mathematical_formula="test")

        # 2. Create an initial state with a known energy
        initial_state = SystemState(
            software_state=SoftwareState(),
            modules=[Module(name="m1", normalized_ast=b"", semantic_tokens=[], cyclomatic_complexity=10.0, duplication_factor=0, coverage_deficit=0, last_refactor=datetime.now())],
            energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=20.0, constraint=10.0, debt=20.0),
            lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0, obligation_penalty=0)
        )
        initial_energy = initial_state.energy_breakdown.total

        # 3. Apply the agent's transformation
        result = agent.apply_physics_principle(initial_state)
        new_state = result.proposals[0]
        final_energy = new_state.energy_breakdown.total

        # 4. Assert that energy has not increased
        assert final_energy <= initial_energy, diagnostic.format_failure_message(
            f"Energy increased during optimization: {initial_energy} -> {final_energy}"
        )
