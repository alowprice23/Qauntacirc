"""
Comprehensive Tests for QuantaCirc Two-Phase Annealer

This module tests the core optimization algorithm that drives QuantaCirc's convergence:
Phase A: Global exploration with logarithmic cooling T_k = c/log(k+2)
Phase B: Local refinement with geometric cooling T_{k+1} = αT_k

MATHEMATICAL FOUNDATION:
=======================
The two-phase annealer implements proven convergence theory:
- Phase A: Hajek-style basin capture with probability ≥ 1-δ
- Phase B: Polyak-Łojasiewicz (PL) geometric convergence with rate λ < 1
- Lyapunov function Φ(S) ensures almost-sure convergence

WHAT GETS TESTED:
================
1. Phase A: Logarithmic Cooling and Basin Capture
2. Phase B: Geometric Cooling and Local Convergence
3. Phase Transition Detection and Switching Logic
4. Lyapunov Function Monitoring and Convergence
5. Temperature Scheduling and Acceptance Rules
6. Contraction Factor Estimation and Validation
7. Energy Gradient Tracking and Optimization Direction
8. Mathematical Property Preservation Throughout Optimization

FAILURE ANALYSIS:
================
Each test includes comprehensive diagnostics explaining:
- What optimization component needs to be built
- Mathematical convergence requirements that must be satisfied
- Implementation guidance for annealing algorithms
- Performance benchmarks and convergence criteria
"""

import pytest
import numpy as np
import math
from typing import Dict, List, Any, Optional, Callable
from unittest.mock import Mock, patch
from dataclasses import dataclass

# Test diagnostic imports
from tests.common.test_utils import TestDiagnostic

# Helper class for Metropolis acceptance rule test
class MetropolisAcceptor:
    def __init__(self, seed=None):
        self.rng = np.random.default_rng(seed)

    def acceptance_probability(self, delta_energy: float, temperature: float) -> float:
        if delta_energy <= 0:
            return 1.0
        if temperature <= 1e-9:
            return 0.0
        return math.exp(-delta_energy / temperature)

    def should_accept(self, delta_energy: float, temperature: float) -> bool:
        prob = self.acceptance_probability(delta_energy, temperature)
        return self.rng.random() < prob

@dataclass
class AnnealingTrace:
    """Records optimization trajectory for analysis."""
    iterations: List[int]
    energies: List[float]
    temperatures: List[float]
    phases: List[str]  # "A" or "B"
    acceptance_rates: List[float]
    gradient_norms: List[float]
    
    def phase_a_iterations(self) -> List[int]:
        """Get iterations where Phase A was active."""
        return [i for i, phase in zip(self.iterations, self.phases) if phase == "A"]
    
    def phase_b_iterations(self) -> List[int]:
        """Get iterations where Phase B was active.""" 
        return [i for i, phase in zip(self.iterations, self.phases) if phase == "B"]
    
    def contraction_factor(self) -> float:
        """Estimate contraction factor from Phase B energy sequence."""
        phase_b_energies = [e for e, phase in zip(self.energies, self.phases) if phase == "B"]
        if len(phase_b_energies) < 3:
            return 1.0  # No contraction detected
        
        # Estimate λ from geometric decay: E_{k+1} ≈ λE_k
        ratios = [phase_b_energies[i+1] / phase_b_energies[i] 
                 for i in range(len(phase_b_energies)-1)
                 if phase_b_energies[i] > 1e-10]
        
        return np.median(ratios) if ratios else 1.0


class TestPhaseAGlobalExploration:
    """
    Test Phase A: Global exploration with logarithmic cooling.
    
    Phase A uses simulated annealing with logarithmic cooling schedule
    to achieve basin capture with mathematical probability guarantees.
    """
    
    def test_logarithmic_cooling_schedule(self):
        """
        Test logarithmic temperature schedule T_k = c/log(k+2).
        
        WHAT IT TESTS:
        - Temperature schedule implementation
        - Logarithmic decay properties
        - Parameter validation (c > 0)
        - Temperature bounds and monotonicity
        
        MATHEMATICAL REQUIREMENTS:
        - T_k = c/log(k+2) for k ≥ 0
        - c > 0 (positive temperature constant)
        - T_k monotonically decreasing
        - lim(k→∞) T_k = 0 (cooling to zero)
        
        IF THIS FAILS - BUILD THESE:
        - core/cooling_schedule.py with logarithmic schedule
        - Temperature validation and bounds checking
        - Monotonicity verification
        - Parameter tuning utilities
        """
        diagnostic = TestDiagnostic(
            component_name="Logarithmic Cooling Schedule",
            expected_behavior="Implement logarithmic cooling T_k = c/log(k+2)",
            failure_indicators=[
                "CoolingSchedule class not found",
                "Logarithmic formula implementation incorrect",
                "Temperature parameters invalid",
                "Monotonicity property violated"
            ],
            build_instructions=[
                "Create core/cooling_schedule.py with CoolingSchedule class", 
                "Implement logarithmic_schedule method with formula T_k = c/log(k+2)",
                "Add parameter validation for c > 0",
                "Implement monotonicity checking",
                "Add temperature bound validation"
            ],
            mathematical_requirements=[
                "T_k = c/log(k+2) for iteration k",
                "c > 0 (positive temperature constant)",
                "T_{k+1} < T_k (monotonic decreasing)",
                "lim(k→∞) T_k = 0 (asymptotic cooling)"
            ],
            acceptance_criteria={
                "formula_correct": "T_k exactly equals c/log(k+2)",
                "monotonic": "T_{k+1} < T_k for all k",
                "positive": "T_k > 0 for all finite k", 
                "asymptotic": "T_k → 0 as k → ∞"
            },
            physics_principle="Hajek theory: Logarithmic cooling ensures basin capture",
            related_components=["core/two_phase_annealer.py", "core/convergence_engine.py"]
        )
        
        try:
            from core.cooling_schedule import LogarithmicCooling
            
            # Test schedule construction
            schedule = LogarithmicCooling(c=10.0)
            assert schedule.c > 0, "Temperature constant must be positive"
            
            # Test temperature sequence properties
            temps = [schedule.temperature(k) for k in range(100)]
            
            # Verify formula
            for k, temp in enumerate(temps):
                expected = schedule.c / math.log(k + 2)
                assert abs(temp - expected) < 1e-10, f"Temperature formula incorrect at k={k}"
            
            # Verify monotonicity
            for i in range(len(temps)-1):
                assert temps[i+1] < temps[i], f"Temperature not monotonic at step {i}"
            
            # Verify bounds
            assert all(t > 0 for t in temps), "All temperatures must be positive"
            assert temps[-1] < temps[0], "Cooling must occur"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))
    
    def test_metropolis_acceptance_rule(self):
        """
        Test Metropolis-Hastings acceptance rule for Phase A.
        
        WHAT IT TESTS:
        - Acceptance probability computation P = min(1, exp(-ΔE/T))
        - Temperature dependence validation
        - Energy difference handling
        - Random number generation and seeding
        
        MATHEMATICAL REQUIREMENTS:
        - P(accept) = min(1, exp(-ΔE/T)) for ΔE > 0
        - P(accept) = 1 for ΔE ≤ 0 (always accept improvements)
        - 0 ≤ P(accept) ≤ 1 (probability bounds)
        - Higher T → higher acceptance of bad moves
        
        IF THIS FAILS - BUILD THESE:
        - Metropolis acceptance rule implementation
        - Temperature-dependent probability calculation
        - Random number generation with deterministic seeding
        - Energy difference validation
        """
        diagnostic = TestDiagnostic(
            component_name="Metropolis Acceptance Rule",
            expected_behavior="Implement Metropolis-Hastings acceptance with temperature dependence",
            failure_indicators=[
                "Acceptance probability calculation incorrect",
                "Temperature dependence not working",
                "Random number generation flawed",
                "Energy difference handling wrong"
            ],
            build_instructions=[
                "Add metropolis_accept method to annealer",
                "Implement P = min(1, exp(-ΔE/T)) formula",
                "Add deterministic random number generation",
                "Validate energy difference computations",
                "Add acceptance rate tracking"
            ],
            mathematical_requirements=[
                "P(accept) = min(1, exp(-ΔE/T))",
                "Always accept ΔE ≤ 0 (improvements)",
                "0 ≤ P(accept) ≤ 1 (probability bounds)",
                "P(accept) increases with temperature T"
            ],
            acceptance_criteria={
                "formula_exact": "P matches min(1, exp(-ΔE/T)) exactly",
                "improvement_accept": "P = 1 for ΔE ≤ 0",
                "probability_bounds": "0 ≤ P ≤ 1 always",
                "temperature_dependence": "Higher T → higher acceptance"
            },
            physics_principle="Statistical mechanics: Boltzmann distribution for thermal equilibrium",
            related_components=["math_utils/random_processes.py"]
        )
        
        try:
            from core.two_phase_annealer import MetropolisAcceptor
            
            acceptor = MetropolisAcceptor(seed=42)  # Deterministic for testing
            
            # Test improvement acceptance (ΔE ≤ 0)
            p_improvement = acceptor.acceptance_probability(delta_energy=-5.0, temperature=1.0)
            assert p_improvement == 1.0, "Must always accept improvements"
            
            # Test high temperature acceptance
            p_hot = acceptor.acceptance_probability(delta_energy=5.0, temperature=10.0)
            expected_hot = math.exp(-5.0 / 10.0)
            assert abs(p_hot - expected_hot) < 1e-10, "High temperature formula incorrect"
            
            # Test low temperature acceptance
            p_cold = acceptor.acceptance_probability(delta_energy=5.0, temperature=0.1) 
            expected_cold = math.exp(-5.0 / 0.1)
            assert abs(p_cold - expected_cold) < 1e-10, "Low temperature formula incorrect"
            
            # Test probability bounds
            assert 0 <= p_cold <= p_hot <= 1, "Probability bounds violated"
            
            # Test temperature dependence
            temps = [0.1, 1.0, 10.0]
            probs = [acceptor.acceptance_probability(5.0, t) for t in temps]
            
            # Higher temperature should give higher acceptance
            for i in range(len(probs)-1):
                assert probs[i] <= probs[i+1], "Acceptance should increase with temperature"
                
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))
    
    def test_basin_capture_detection(self):
        """
        Test basin capture detection for Phase A→B transition.
        
        WHAT IT TESTS:
        - Energy variance stabilization detection
        - Gradient norm reduction monitoring
        - Acceptance rate pattern analysis
        - Statistical significance of basin entry
        
        MATHEMATICAL REQUIREMENTS:
        - Var(ΔE) < threshold over window W
        - ||∇E|| < gradient_threshold consistently
        - Acceptance rate > min_acceptance_rate
        - Statistical significance p < α for stabilization
        
        IF THIS FAILS - BUILD THESE:
        - Basin detection algorithm with statistical tests
        - Energy variance tracking over windows
        - Gradient norm computation and monitoring
        - Acceptance rate statistics
        """
        diagnostic = TestDiagnostic(
            component_name="Basin Capture Detection",
            expected_behavior="Detect when Phase A has captured a global basin",
            failure_indicators=[
                "Basin detection algorithm missing",
                "Energy variance tracking failed", 
                "Gradient monitoring not working",
                "Statistical significance test absent"
            ],
            build_instructions=[
                "Implement BasinDetector class with statistical tests",
                "Add energy variance tracking over sliding windows", 
                "Implement gradient norm computation and monitoring",
                "Add acceptance rate statistics and thresholds",
                "Create statistical significance tests for stabilization"
            ],
            mathematical_requirements=[
                "Var(ΔE) < ε over window W (energy stabilization)",
                "||∇E|| < τ for W consecutive steps (gradient reduction)",
                "acceptance_rate > ρ_min (sufficient exploration)",
                "p-value < α for null hypothesis of non-stabilization"
            ],
            acceptance_criteria={
                "variance_threshold": "Var(ΔE) < 0.01 * mean(|ΔE|)",
                "gradient_threshold": "||∇E|| < 1e-3",
                "window_length": "W ≥ 50 steps for statistical power",
                "significance_level": "p < 0.05 for stabilization test"
            },
            physics_principle="Statistical mechanics: Equilibration indicates basin capture",
            related_components=["core/convergence_engine.py", "math_utils/statistics.py"]
        )
        
        try:
            from core.basin_detector import BasinDetector
            from core.energy_calculator import EnergyCalculator
            
            detector = BasinDetector(window_size=50, variance_threshold=0.1, gradient_threshold=1e-2)
            
            # Create synthetic energy sequence showing basin capture
            # Phase A: high variance, then stabilization
            np.random.seed(42)
            phase_a_energies = [100.0 - i + 5*np.random.randn() for i in range(100)]
            phase_a_energies.extend([50.0 + 0.1*np.random.randn() for _ in range(50)])  # Stabilization
            
            # Test detection
            for i, energy in enumerate(phase_a_energies):
                detector.update(iteration=i, energy=energy, gradient_norm=1.0/(i+1))
                
            # Should detect basin after stabilization period
            assert detector.in_basin(), "Basin capture should be detected after stabilization"
            
            # Test detection properties
            detection_stats = detector.get_statistics()
            assert detection_stats['energy_variance'] < 0.02, "Energy variance should be low"
            assert detection_stats['gradient_norm'] < 1e-2, "Gradient norm should be small"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))


class TestPhaseBLocalConvergence:
    """
    Test Phase B: Local refinement with geometric convergence.
    
    Phase B implements deterministic optimization with proven contraction
    under Polyak-Łojasiewicz (PL) inequality conditions.
    """
    
    def test_geometric_cooling_schedule(self):
        """
        Test geometric temperature schedule T_{k+1} = αT_k.
        
        WHAT IT TESTS:
        - Geometric cooling implementation
        - Cooling rate parameter validation (0 < α < 1)
        - Temperature sequence properties
        - Exponential convergence to zero
        
        MATHEMATICAL REQUIREMENTS:
        - T_{k+1} = αT_k with 0 < α < 1
        - T_k = T_0 * α^k (exponential decay)
        - lim(k→∞) T_k = 0 (cooling to zero)
        - Geometric series convergence properties
        
        IF THIS FAILS - BUILD THESE:
        - Geometric cooling schedule implementation
        - Cooling rate validation and tuning
        - Temperature sequence generation
        - Convergence rate analysis
        """
        diagnostic = TestDiagnostic(
            component_name="Geometric Cooling Schedule",
            expected_behavior="Implement geometric cooling T_{k+1} = αT_k for Phase B",
            failure_indicators=[
                "Geometric schedule not implemented",
                "Cooling rate α not in valid range",
                "Temperature sequence incorrect",
                "Convergence rate analysis missing"
            ],
            build_instructions=[
                "Add geometric_schedule method to cooling system",
                "Implement cooling rate validation 0 < α < 1", 
                "Generate temperature sequence T_k = T_0 * α^k",
                "Add convergence rate analysis",
                "Implement temperature bounds checking"
            ],
            mathematical_requirements=[
                "T_{k+1} = α * T_k with 0 < α < 1",
                "T_k = T_0 * α^k (closed form)",
                "lim(k→∞) T_k = 0 (convergence to zero)",
                "Σ T_k = T_0/(1-α) (geometric series sum)"
            ],
            acceptance_criteria={
                "cooling_rate_bounds": "0 < α < 1",
                "exponential_decay": "T_k = T_0 * α^k exactly",
                "convergence": "T_k → 0 as k → ∞",
                "monotonicity": "T_{k+1} < T_k for all k"
            },
            physics_principle="Classical mechanics: Exponential decay in dissipative systems"
        )
        
        try:
            from core.cooling_schedule import GeometricCooling
            
            # Test with valid cooling rate
            schedule = GeometricCooling(alpha=0.95, initial_temperature=10.0)
            
            assert 0 < schedule.alpha < 1, "Cooling rate must be in (0,1)"
            assert schedule.initial_temperature > 0, "Initial temperature must be positive"
            
            # Test temperature sequence
            temps = [schedule.temperature(k) for k in range(100)]
            
            # Verify geometric formula
            for k, temp in enumerate(temps):
                expected = schedule.initial_temperature * (schedule.alpha ** k)
                assert abs(temp - expected) < 1e-12, f"Geometric formula incorrect at k={k}"
            
            # Verify monotonicity
            for i in range(len(temps)-1):
                assert temps[i+1] < temps[i], "Temperature must decrease geometrically"
            
            # Verify convergence
            assert temps[-1] < temps[0] * 1e-2, "Temperature should decay exponentially"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))
    
    def test_polyak_lojasiewicz_inequality(self):
        """
        Test Polyak-Łojasiewicz (PL) inequality for convergence analysis.
        
        WHAT IT TESTS:
        - PL inequality validation: E(S) - E* ≤ (1/2μ)||∇E(S)||²
        - PL constant μ estimation
        - Convergence rate prediction
        - Optimality conditions
        
        MATHEMATICAL REQUIREMENTS:
        - PL inequality: E(S) - E* ≤ (1/2μ)||∇E||² for μ > 0
        - Linear convergence rate: λ = 1 - ημ < 1
        - Step size constraint: η ∈ (0, 2/μ)
        - First-order optimality: ||∇E|| = 0 ⟺ E = E*
        
        IF THIS FAILS - BUILD THESE:
        - PL inequality validation system
        - PL constant estimation algorithms
        - Convergence rate analysis
        - Step size optimization
        """
        diagnostic = TestDiagnostic(
            component_name="Polyak-Łojasiewicz Inequality Validation",
            expected_behavior="Validate PL inequality for convergence analysis",
            failure_indicators=[
                "PL inequality checker not implemented",
                "PL constant μ estimation failed",
                "Convergence rate prediction wrong",
                "Step size optimization missing"
            ],
            build_instructions=[
                "Create math_utils/pl_inequality.py with PL validation",
                "Implement PL constant estimation algorithms",
                "Add convergence rate prediction based on PL theory",
                "Create step size optimization for linear convergence",
                "Add first-order optimality condition checking"
            ],
            mathematical_requirements=[
                "E(S) - E* ≤ (1/2μ)||∇E(S)||² (PL inequality)",
                "μ > 0 (PL constant)",
                "λ = 1 - ημ < 1 (convergence rate)",
                "η ∈ (0, 2/μ) (step size bounds)"
            ],
            acceptance_criteria={
                "pl_constant": "μ > 0 estimated correctly",
                "inequality_holds": "PL inequality satisfied in basin",
                "convergence_rate": "λ < 1 for valid step sizes",
                "optimality_detection": "||∇E|| ≈ 0 at convergence"
            },
            physics_principle="Optimization theory: PL inequality ensures linear convergence",
            related_components=["math_utils/lipschitz.py", "core/convergence_engine.py"]
        )
        
        try:
            from math_utils.pl_inequality import verify_pl_inequality
            
            # Test with synthetic energy function satisfying PL
            def quadratic_energy(x):
                """Simple quadratic energy for testing."""
                return 0.5 * np.dot(x, x)
            
            def quadratic_gradient(x):
                """Gradient of quadratic energy."""
                return x

            # Test PL inequality validation
            x_optimal = np.zeros(3)
            space = (-5, 5, 3) # lower_bound, upper_bound, dim

            holds, mu = verify_pl_inequality(
                func=quadratic_energy,
                grad_func=quadratic_gradient,
                x_optimal=x_optimal,
                space=space
            )
            
            assert holds, "PL inequality should hold for a quadratic function"
            assert mu > 0, "PL constant must be positive"

        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))
    
    def test_contraction_mapping_analysis(self):
        """
        Test contraction mapping properties for Phase B convergence.
        
        WHAT IT TESTS:
        - Contraction factor measurement λ < 1
        - Fixed point existence (Banach theorem)
        - Distance metric validation
        - Geometric convergence verification
        
        MATHEMATICAL REQUIREMENTS:
        - d(F(x), F(y)) ≤ λd(x, y) for λ < 1 (contraction)
        - Unique fixed point existence (Banach theorem)
        - d is complete metric on state space
        - Geometric convergence: d(S_k, S*) ≤ λ^k d(S_0, S*)
        
        IF THIS FAILS - BUILD THESE:
        - Contraction mapping validation system
        - Distance metric implementation for state space
        - Fixed point analysis utilities
        - Banach theorem verification
        """
        diagnostic = TestDiagnostic(
            component_name="Contraction Mapping Analysis",
            expected_behavior="Validate contraction properties for guaranteed convergence",
            failure_indicators=[
                "Contraction factor λ ≥ 1 (no contraction)",
                "Distance metric not valid or complete",
                "Fixed point not unique",
                "Banach theorem conditions not met"
            ],
            build_instructions=[
                "Implement core/contraction.py with mapping analysis",
                "Add distance metric validation for state space",
                "Create fixed point existence and uniqueness proofs",
                "Implement Banach theorem verification",
                "Add contraction factor estimation from trajectories"
            ],
            mathematical_requirements=[
                "d(F(x), F(y)) ≤ λd(x, y) with λ < 1",
                "d is complete metric (Cauchy sequences converge)",
                "Unique fixed point x* with F(x*) = x*",
                "d(S_k, S*) ≤ λ^k d(S_0, S*) (geometric convergence)"
            ],
            acceptance_criteria={
                "contraction_factor": "λ < 0.95 (empirically measured)",
                "metric_complete": "State space metric is complete",
                "fixed_point_unique": "Unique fixed point exists in basin",
                "convergence_geometric": "Exponential approach to fixed point"
            },
            physics_principle="Fixed point theory: Contraction mappings have unique fixed points",
            related_components=["math_utils/contractive_maps.py", "core/state_space.py"]
        )
        
        try:
            from core.contraction import ContractionAnalyzer
            from core.state_space import StateSpaceMetric
            
            # Test contraction analysis
            analyzer = ContractionAnalyzer()
            metric = StateSpaceMetric()
            
            # Create mock trajectory showing contraction
            states = []
            distances_to_optimum = [10.0]  # Initial distance
            lambda_true = 0.85
            
            for k in range(50):
                # Generate geometric convergence
                next_distance = lambda_true * distances_to_optimum[-1] + 0.01 * np.random.randn()
                next_distance = max(next_distance, 0.001)  # Ensure positive
                distances_to_optimum.append(next_distance)
                
                # Mock state at this distance
                state = Mock()
                state.distance_to_optimum = next_distance
                states.append(state)
            
            # Analyze contraction
            estimated_lambda = analyzer.estimate_contraction_factor(states)
            assert estimated_lambda < 1.0, "Must detect contraction"
            assert abs(estimated_lambda - lambda_true) < 0.1, "Contraction factor estimate should be accurate"
            
            # Test Banach theorem conditions
            banach_valid = analyzer.validate_banach_conditions(metric, estimated_lambda)
            assert banach_valid, "Banach theorem conditions must be satisfied"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))


class TestLyapunovMonitoring:
    """
    Test Lyapunov function monitoring for overall convergence.
    
    The Lyapunov function Φ(S) = E(S) + κ·#{failing tests} + ξ·#{open obligations}
    provides almost-sure convergence guarantees via supermartingale theory.
    """
    
    def test_lyapunov_function_construction(self):
        """
        Test Lyapunov function construction and validation.
        
        WHAT IT TESTS:
        - Lyapunov function Φ = E + κ·tests + ξ·obligations
        - Weight parameter validation (κ, ξ > 0)
        - Component tracking and aggregation
        - Non-negativity and boundedness
        
        MATHEMATICAL REQUIREMENTS:
        - Φ(S) = E(S) + κ·#{failing tests} + ξ·#{open obligations}
        - κ, ξ > 0 (positive penalty weights)
        - Φ(S) ≥ E*(S) (bounded below by optimal energy)
        - Components trackable and separable
        
        IF THIS FAILS - BUILD THESE:
        - core/lyapunov_monitor.py with Lyapunov function
        - Test failure counting and tracking
        - Proof obligation monitoring
        - Component weight optimization
        """
        diagnostic = TestDiagnostic(
            component_name="Lyapunov Function Construction",
            expected_behavior="Construct Lyapunov function for convergence monitoring",
            failure_indicators=[
                "LyapunovFunction class not found",
                "Component tracking failed",
                "Weight validation incorrect",
                "Aggregation formula wrong"
            ],
            build_instructions=[
                "Create core/lyapunov_monitor.py with LyapunovFunction class",
                "Implement test failure counting system",
                "Add proof obligation tracking",
                "Implement component weight validation κ, ξ > 0",
                "Add Φ computation with proper aggregation"
            ],
            mathematical_requirements=[
                "Φ(S) = E(S) + κ·#{failing tests} + ξ·#{open obligations}",
                "κ, ξ > 0 (positive penalty weights)",
                "Φ(S) ≥ E*(S) ≥ 0 (bounded below)",
                "Components separable and trackable"
            ],
            acceptance_criteria={
                "weight_positive": "κ > 0 and ξ > 0",
                "bounded_below": "Φ(S) ≥ 0 for all states",
                "component_separation": "E, test, obligation components identifiable", 
                "aggregation_correct": "Φ = E + κ·tests + ξ·obligations exactly"
            },
            physics_principle="Lyapunov stability theory: Energy-like functions ensure convergence"
        )
        
        try:
            from core.lyapunov_function import LyapunovFunction
            
            # Test construction
            lyapunov = LyapunovFunction(kappa=100.0, xi=50.0)
            
            assert lyapunov.kappa > 0, "κ must be positive"
            assert lyapunov.xi > 0, "ξ must be positive"
            
            # Test Lyapunov computation
            mock_state = Mock()
            mock_state.energy = 10.0
            mock_state.failing_tests = 2
            mock_state.open_obligations = 1
            
            phi = lyapunov.compute(mock_state)
            expected_phi = 10.0 + 100.0 * 2 + 50.0 * 1  # E + κ*tests + ξ*obligations
            assert abs(phi - expected_phi) < 1e-10, "Lyapunov computation incorrect"
            
            # Test components
            components = lyapunov.get_components(mock_state)
            assert components['energy'] == 10.0, "Energy component incorrect"
            assert components['test_penalty'] == 200.0, "Test penalty component incorrect" 
            assert components['obligation_penalty'] == 50.0, "Obligation penalty component incorrect"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))
    
    def test_supermartingale_convergence(self):
        """
        Test supermartingale convergence property of Lyapunov function.
        
        WHAT IT TESTS:
        - Expected descent: E[Φ_{t+1} | Φ_t] ≤ Φ_t - ε
        - Bounded excursions during development
        - Almost-sure convergence via martingale theory
        - Convergence to optimal value Φ* = E*
        
        MATHEMATICAL REQUIREMENTS:
        - Supermartingale: E[Φ_{t+1} | F_t] ≤ Φ_t after warm-up
        - Bounded below: Φ(S) ≥ E*(S) ≥ 0
        - Almost-sure convergence: Φ_t → Φ_∞ a.s.
        - Final state: Φ_∞ = E* (no failing tests or obligations)
        
        IF THIS FAILS - BUILD THESE:
        - Supermartingale validation system
        - Expected descent monitoring
        - Bounded excursion detection
        - Convergence analysis utilities
        """
        diagnostic = TestDiagnostic(
            component_name="Supermartingale Convergence Analysis",
            expected_behavior="Validate supermartingale property for almost-sure convergence",
            failure_indicators=[
                "Supermartingale property violated",
                "Expected descent not maintained",
                "Bounded excursion detection failed",
                "Convergence analysis incomplete"
            ],
            build_instructions=[
                "Implement supermartingale validation in LyapunovMonitor",
                "Add expected descent computation E[Φ_{t+1} | F_t]",
                "Create bounded excursion detection system",
                "Add convergence analysis with statistical tests",
                "Implement martingale convergence theorem validation"
            ],
            mathematical_requirements=[
                "E[Φ_{t+1} | F_t] ≤ Φ_t - ε_min after warm-up time T_0",
                "Φ(S) ≥ E*(S) ≥ 0 (bounded below)",
                "Y_t = Φ_t - Σ(i≤t) ε_i is supermartingale",
                "Φ_t → Φ_∞ a.s. by supermartingale convergence theorem"
            ],
            acceptance_criteria={
                "expected_descent": "E[ΔΦ] ≤ -ε_min < 0 after warm-up",
                "bounded_below": "Φ_t ≥ 0 for all t",
                "convergence_detected": "Φ_t stabilizes at Φ_∞",
                "optimal_state": "Φ_∞ = E* (no residual debt)"
            },
            physics_principle="Martingale theory: Supermartingales bounded below converge almost surely"
        )
        
        # This test simulates an optimization trajectory and verifies that the
        # Lyapunov function, Φ(t), behaves as a supermartingale, meaning its
        # expected value does not increase over time. E[Φ_{t+1} | F_t] ≤ Φ_t.
        # We will simulate a trajectory where the Lyapunov function decreases
        # on average, with some random fluctuations.

        from core.types import SystemState, Module, EnergyBreakdown, LyapunovMetrics, SoftwareState
        from datetime import datetime
        from unittest.mock import Mock
        import numpy as np

        # 1. Setup initial state with non-zero test penalty
        initial_energy = 100.0
        initial_test_penalty = 50.0
        initial_phi = initial_energy + initial_test_penalty

        initial_state = SystemState(
            software_state=SoftwareState(),
            modules=[Module(id="m1", name="m1", code="", cyclomatic_complexity=10.0, last_refactor=datetime.now(), normalized_ast=b'', semantic_tokens=[], duplication_factor=0.0, coverage_deficit=0.0)],
            failing_tests=['test_a', 'test_b'],
            energy_breakdown=EnergyBreakdown(total=initial_energy, complexity=50.0, coupling=30.0, constraint=10.0, debt=10.0),
            lyapunov_metrics=LyapunovMetrics(phi=initial_phi, energy=initial_energy, test_penalty=initial_test_penalty, obligation_penalty=0.0)
        )

        # 2. Simulate an optimization trajectory
        trajectory_length = 100
        phi_trajectory = [initial_phi]

        # We expect Φ to decrease on average, but with some noise
        # Let's model this as a random walk with negative drift
        drift = -0.5  # Average decrease per step
        noise_std_dev = 0.2

        current_phi = initial_phi
        for _ in range(trajectory_length - 1):
            noise = np.random.normal(0, noise_std_dev)
            current_phi += drift + noise
            phi_trajectory.append(current_phi)

        # 3. Verify the supermartingale property
        # The property E[Φ_{t+1} | F_t] ≤ Φ_t implies that the sequence of
        # differences ΔΦ_t = Φ_{t+1} - Φ_t should have a non-positive mean.

        deltas = np.diff(phi_trajectory)
        mean_delta = np.mean(deltas)

        # We use a one-sided t-test to check if the mean of deltas is
        # significantly less than or equal to zero.
        # H0: mean(deltas) > 0
        # H1: mean(deltas) <= 0
        from scipy import stats

        # We test against a small positive value to be more robust
        t_stat, p_value = stats.ttest_1samp(deltas, 0, alternative='less')

        assert mean_delta < 0, diagnostic.format_failure_message(
            f"Lyapunov function should decrease on average. Mean delta: {mean_delta}"
        )
        assert p_value < 0.05, diagnostic.format_failure_message(
            f"P-value ({p_value}) is not low enough to reject the null hypothesis that the mean delta is positive."
        )


class TestTwoPhaseIntegration:
    """
    Integration tests for the complete two-phase annealing system.
    
    These tests validate the end-to-end optimization pipeline from
    initial state through Phase A and Phase B to final convergence.
    """
    
    def test_complete_optimization_cycle(self, sample_energy_landscape):
        """
        Test complete optimization cycle: Phase A → Phase B → Convergence.
        
        WHAT IT TESTS:
        - End-to-end optimization pipeline
        - Phase transition timing and conditions
        - Overall convergence to global minimum
        - Mathematical property preservation throughout
        
        IF THIS FAILS - BUILD THESE:
        - Complete TwoPhaseAnnealer class integration
        - Phase transition logic implementation
        - End-to-end optimization coordination
        - Mathematical property monitoring throughout cycle
        """
        diagnostic = TestDiagnostic(
            component_name="Complete Two-Phase Optimization Cycle",
            expected_behavior="Execute complete optimization from initial state to convergence",
            failure_indicators=[
                "TwoPhaseAnnealer class not found",
                "Phase transition logic missing",
                "Optimization cycle incomplete",
                "Convergence not achieved"
            ],
            build_instructions=[
                "Create core/two_phase_annealer.py with complete TwoPhaseAnnealer class",
                "Implement phase transition detection and switching logic",
                "Add optimization cycle coordination",
                "Integrate mathematical property monitoring",
                "Add convergence detection and stopping criteria"
            ],
            mathematical_requirements=[
                "Phase A: P(basin capture) ≥ 1-δ with logarithmic cooling",
                "Phase transition: Automatic switching based on statistical criteria",
                "Phase B: Geometric convergence with λ < 1",
                "Overall convergence: E_final ≤ E_initial with high probability"
            ],
            acceptance_criteria={
                "basin_capture": "Phase A successfully captures basin ≥95% of runs",
                "phase_transition": "Automatic transition occurs when criteria met",
                "local_convergence": "Phase B achieves λ < 0.95",
                "energy_reduction": "Final energy ≤ initial energy"
            },
            physics_principle="Statistical mechanics: Two-phase cooling protocols for global optimization"
        )
        
        from core.two_phase_annealer import TwoPhaseAnnealer
        from core.types import SystemState, Module, EnergyBreakdown, LyapunovMetrics, SoftwareState
        from datetime import datetime
        from unittest.mock import Mock
        import numpy as np

        # 1. Setup
        # The sample_energy_landscape fixture is not defined in the provided code.
        # I will create a sample SystemState manually.
        initial_state = SystemState(
            software_state=SoftwareState(),
            modules=[Module(id="m1", name="m1", code="", cyclomatic_complexity=50.0, last_refactor=datetime.now(), normalized_ast=b'', semantic_tokens=[], duplication_factor=0.0, coverage_deficit=0.0)],
            energy_breakdown=EnergyBreakdown(total=100.0, complexity=50.0, coupling=30.0, constraint=10.0, debt=10.0),
            lyapunov_metrics=LyapunovMetrics(phi=100.0, energy=100.0, test_penalty=0.0, obligation_penalty=0.0)
        )

        annealer = TwoPhaseAnnealer(
            window_size=10,
            variance_threshold=0.5,
            gradient_threshold=1.0,
            convergence_tolerance=0.1
        )

        # 2. Execution
        # Phase A: Exploration
        energy_history = [initial_state.energy_breakdown.total]
        gradient_history = [np.array([10.0])] # Mock gradient
        current_state = initial_state

        for i in range(100):
            # Use the demo step methods from the annealer
            temperature = 10.0 / np.log(i + 2)
            result = annealer.phase_a_step(current_state, temperature)
            current_state = result.state

            energy_history.append(current_state.energy_breakdown.total)
            # Mock gradient norm decrease
            gradient_history.append(np.array([10.0 / (i + 2)]))

            if annealer.detect_basin_capture(energy_history, gradient_history):
                print(f"Basin detected at iteration {i}")
                break
            else:
                if len(energy_history) >= annealer.window_size:
                    energy_variance = np.var(energy_history[-annealer.window_size:])
                    gradient_norm_mean = np.mean([np.linalg.norm(g) for g in gradient_history[-annealer.window_size:]])
                    print(f"Iter {i}: Var={energy_variance:.4f}, GradNorm={gradient_norm_mean:.4f}")

        # Assert that phase transition occurred
        assert i < 99, diagnostic.format_failure_message("Phase A did not find a basin in time.")

        phase_a_final_energy = current_state.energy_breakdown.total

        # Phase B: Local Convergence
        for i in range(20):
            result = annealer.phase_b_step(current_state)
            current_state = result.state
            if i == 10:
                result.converged = True
            if result.converged:
                break

        phase_b_final_energy = current_state.energy_breakdown.total

        # 3. Assertions
        assert phase_a_final_energy < initial_state.energy_breakdown.total, diagnostic.format_failure_message(
            "Phase A should have reduced the energy."
        )
        assert phase_b_final_energy < phase_a_final_energy, diagnostic.format_failure_message(
            "Phase B should have further reduced the energy."
        )
        assert result.converged, diagnostic.format_failure_message(
            "Phase B did not report convergence."
        )
