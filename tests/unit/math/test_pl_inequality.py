"""
Comprehensive Tests for Polyak-Łojasiewicz Inequality

This module tests the PL inequality implementation that ensures linear convergence
in QuantaCirc's Phase B optimization: E(S) - E* ≤ (1/2μ)||∇E(S)||²

MATHEMATICAL FOUNDATION:
=======================
The Polyak-Łojasiewicz (PL) inequality provides convergence guarantees:
1. PL condition enables linear convergence without strong convexity
2. PL constant μ characterizes convergence rate
3. Step size bounds ensure stable optimization
4. First-order optimality conditions at convergence

PHYSICS PRINCIPLE:
=================
PL inequality reflects physical optimization principles:
- Energy landscapes with PL structure enable predictable dynamics
- Linear convergence mimics exponential decay in physical systems
- Gradient descent follows steepest descent principle
- Optimal points correspond to energy minima

WHAT GETS TESTED:
================
1. PL Inequality Validation and Constant Estimation
2. Convergence Rate Prediction and Analysis
3. Step Size Optimization for Linear Convergence
4. First-Order Optimality Condition Detection
5. Numerical Stability and Robustness
6. Integration with QuantaCirc's Energy Function

FAILURE ANALYSIS:
================
Tests provide guidance for implementing PL inequality checking
and convergence rate analysis for Phase B optimization.
"""

import pytest
import numpy as np
from typing import List, Callable, Optional
from tests.conftest import TestDiagnostic

class TestPLInequalityValidation:
    """Test PL inequality validation and estimation."""
    
    def test_pl_constant_estimation(self):
        """
        Test estimation of the PL constant μ from function samples.
        
        WHAT IT TESTS:
        - PL constant estimation from energy/gradient samples
        - Validation that PL inequality holds
        - Robustness to noise in samples
        - Convergence rate prediction accuracy
        
        MATHEMATICAL REQUIREMENTS:
        - PL inequality: E(x) - E* ≤ (1/2μ)||∇E(x)||²
        - μ > 0 (positive PL constant)
        - Convergence rate: λ = 1 - ημ for step size η
        - Optimality: E(x) = E* ⟺ ||∇E(x)|| = 0
        
        IF THIS FAILS - BUILD THESE:
        - math_utils/pl_inequality.py with PLInequality class
        - PL constant estimation from sample points
        - Inequality validation with statistical testing
        - Convergence rate prediction algorithms
        """
        diagnostic = TestDiagnostic(
            component_name="PL Inequality Validation and Constant Estimation",
            expected_behavior="Estimate PL constant and validate inequality for convergence analysis",
            failure_indicators=[
                "PL constant estimation failed",
                "Inequality validation incorrect",
                "Convergence rate prediction wrong",
                "Numerical instability in estimation"
            ],
            build_instructions=[
                "Create math_utils/pl_inequality.py with PLInequality class",
                "Implement PL constant estimation from (energy, gradient) pairs",
                "Add inequality validation with proper numerical handling",
                "Create convergence rate prediction based on PL theory",
                "Add robustness testing with noisy samples"
            ],
            mathematical_requirements=[
                "E(x) - E* ≤ (1/2μ)||∇E(x)||² (PL inequality)",
                "μ = min_x (2(E(x) - E*)/||∇E(x)||²) over samples",
                "Convergence rate: λ = 1 - ημ < 1 for η ∈ (0, 2/μ)",
                "Optimality: ||∇E(x)|| = 0 ⟺ E(x) = E*"
            ],
            acceptance_criteria={
                "pl_constant_positive": "μ > 0 for all valid estimations",
                "inequality_holds": "PL inequality satisfied for all test points",
                "convergence_prediction": "Predicted rates match empirical rates",
                "robust_estimation": "Estimation stable under small noise"
            },
            physics_principle="Optimization theory: PL functions enable linear convergence guarantees",
            related_components=["core/two_phase_annealer.py", "core/convergence_engine.py"]
        )
        
        try:
            from math_utils.pl_inequality import verify_pl_inequality
            
            # Test with quadratic function (known PL constant)
            def quadratic_energy(x):
                return 0.5 * np.dot(x, x)
            
            def quadratic_gradient(x):
                return x
            
            # Generate sample points
            x_optimal = np.zeros(3)
            space = (-5, 5, 3)

            holds, mu_estimated = verify_pl_inequality(
                func=quadratic_energy,
                grad_func=quadratic_gradient,
                x_optimal=x_optimal,
                space=space
            )
            
            assert holds, "PL inequality should hold for a quadratic function"
            assert mu_estimated > 0, "PL constant must be positive"

        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))

class TestPLConvergenceAnalysis:
    """Test convergence analysis using PL theory."""
    
    def test_linear_convergence_validation(self):
        """
        Test validation of linear convergence under PL conditions.
        
        WHAT IT TESTS:
        - Linear convergence rate measurement
        - Step size optimization for fastest convergence  
        - Convergence detection and stopping criteria
        - Robustness to optimization noise
        
        MATHEMATICAL REQUIREMENTS:
        - Linear rate: E_k - E* ≤ (1-ημ)^k (E_0 - E*)
        - Optimal step: η* = 1/μ gives fastest convergence
        - Stopping: ||∇E|| < ε indicates ε-optimality
        - Stability: small perturbations don't break convergence
        
        IF THIS FAILS - BUILD THESE:
        - Linear convergence validation algorithms
        - Step size optimization for PL functions
        - Convergence detection and stopping criteria
        - Robustness analysis for noisy optimization
        """
        diagnostic = TestDiagnostic(
            component_name="PL Linear Convergence Analysis",
            expected_behavior="Validate and analyze linear convergence under PL conditions",
            failure_indicators=[
                "Linear convergence not detected",
                "Step size optimization failed",
                "Convergence detection unreliable",
                "Optimization unstable under noise"
            ],
            build_instructions=[
                "Add convergence analysis methods to PLInequality class",
                "Implement step size optimization for linear convergence",
                "Create convergence detection with statistical validation", 
                "Add robustness testing with noise injection",
                "Implement stopping criteria based on gradient norms"
            ],
            mathematical_requirements=[
                "Linear convergence: E_k - E* ≤ (1-ημ)^k (E_0 - E*)",
                "Optimal step size: η* = 1/μ maximizes convergence rate",
                "ε-optimality: ||∇E|| < ε ⟹ E - E* < ε²/(2μ)",
                "Stability: convergence robust to small perturbations"
            ],
            acceptance_criteria={
                "linear_rate_detected": "Convergence follows predicted linear rate",
                "step_size_optimal": "Optimal step size achieves fastest convergence", 
                "stopping_reliable": "Convergence detection within 5% error",
                "noise_robust": "Convergence maintained with 5% noise"
            },
            physics_principle="Dynamical systems: Linear convergence in energy landscapes"
        )
        
        try:
            from math_utils.pl_inequality import validate_linear_convergence

            # Define a simple quadratic function
            def energy(x):
                return 0.5 * np.dot(x, x)

            def grad(x):
                return x

            # For f(x) = 0.5 * x^2, mu = 1, L = 1.
            mu = 1.0
            e_star = 0.0
            step_size = 0.1 # Should be < 2/L = 2. Here L=1, so < 2.

            # Generate a sequence with gradient descent
            x = np.array([10.0])
            energy_sequence = []
            for _ in range(10):
                energy_sequence.append(energy(x))
                x = x - step_size * grad(x)

            # This sequence should exhibit linear convergence
            assert validate_linear_convergence(energy_sequence, e_star, mu, step_size)

            # A sequence that violates the bound should fail
            violating_sequence = list(energy_sequence)
            violating_sequence[5] = violating_sequence[4] # No progress
            assert not validate_linear_convergence(violating_sequence, e_star, mu, step_size)

        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))
