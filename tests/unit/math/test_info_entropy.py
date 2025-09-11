"""
Comprehensive Tests for Information Entropy Utilities

This module tests Shannon entropy calculation and information-theoretic measures
that form the foundation of QuantaCirc's complexity energy calculation.

MATHEMATICAL FOUNDATION:
=======================
Shannon entropy H(X) = -Σᵢ p(xᵢ) log p(xᵢ) measures the information content
of a random variable. In QuantaCirc, entropy quantifies:
1. Code complexity through token distribution analysis
2. Semantic information content in specifications
3. Uncertainty reduction through optimization
4. Information bounds via compression theory

PHYSICS PRINCIPLE:
=================
Information theory connects to thermodynamics through:
- Entropy as measure of disorder/information content
- Maxwell-Boltzmann distribution for probability assignments
- Landauer's principle linking information and energy
- Second law of thermodynamics: entropy tends to increase

WHAT GETS TESTED:
================
1. Shannon Entropy Calculation and Validation
2. Conditional Entropy and Mutual Information
3. Cross-Entropy and KL Divergence
4. Information Bounds and Compression Limits
5. Entropy Rate for Stochastic Processes
6. Information-Theoretic Complexity Measures

FAILURE ANALYSIS:
================
Tests provide guidance on building information-theoretic components
for QuantaCirc's complexity energy calculations.
"""

import pytest
import numpy as np
import math
from typing import List, Dict, Any
from collections import Counter

from tests.conftest import TestDiagnostic


class TestShannonEntropy:
    """Test Shannon entropy calculation and properties."""
    
    def test_entropy_calculation_discrete(self):
        """
        Test Shannon entropy calculation for discrete distributions.
        
        MATHEMATICAL REQUIREMENTS:
        - H(X) = -Σᵢ p(xᵢ) log₂ p(xᵢ)
        - 0 ≤ H(X) ≤ log₂ |X| (entropy bounds)
        - H(X) = 0 iff X deterministic
        - H(X) = log₂ |X| iff X uniform
        """
        diagnostic = TestDiagnostic(
            component_name="Shannon Entropy Calculation",
            expected_behavior="Calculate Shannon entropy for discrete probability distributions",
            failure_indicators=[
                "shannon_entropy function not found",
                "Probability normalization failed",
                "Log base handling incorrect", 
                "Entropy bounds violated"
            ],
            build_instructions=[
                "Create math_utils/info_entropy.py with shannon_entropy function",
                "Implement probability distribution validation and normalization",
                "Add support for different log bases (base 2, e, 10)",
                "Implement entropy bounds checking",
                "Add special case handling (zero probabilities, single outcomes)"
            ],
            mathematical_requirements=[
                "H(X) = -Σᵢ p(xᵢ) log₂ p(xᵢ)",
                "0 ≤ H(X) ≤ log₂ |X| (fundamental bounds)",
                "H(X) = 0 ⟺ ∃i: p(xᵢ) = 1 (deterministic)",
                "H(X) = log₂ |X| ⟺ ∀i: p(xᵢ) = 1/|X| (uniform)"
            ],
            acceptance_criteria={
                "bounds_satisfied": "0 ≤ H(X) ≤ log₂ |X|",
                "deterministic_zero": "H = 0 for deterministic distributions",
                "uniform_maximum": "H = log₂ n for uniform distribution over n outcomes",
                "numerical_stability": "Correct handling of zero probabilities"
            },
            physics_principle="Statistical mechanics: Entropy measures microscopic disorder"
        )
        
        try:
            from math_utils.info_entropy import shannon_entropy
            
            # Test uniform distribution (maximum entropy)
            uniform_probs = np.array([0.25, 0.25, 0.25, 0.25])
            uniform_entropy = shannon_entropy(uniform_probs)
            expected_uniform = 2.0  # log₂(4)
            assert abs(uniform_entropy - expected_uniform) < 1e-10, "Uniform entropy incorrect"
            
            # Test deterministic distribution (zero entropy)
            deterministic_probs = np.array([1.0, 0.0, 0.0, 0.0])
            deterministic_entropy = shannon_entropy(deterministic_probs)
            assert abs(deterministic_entropy) < 1e-10, "Deterministic entropy should be zero"
            
            # Test skewed distribution
            skewed_probs = [0.8, 0.1, 0.05, 0.05]
            skewed_entropy = shannon_entropy(skewed_probs)
            assert 0 < skewed_entropy < 2.0, "Skewed entropy should be between 0 and max"
            assert skewed_entropy < uniform_entropy, "Skewed should have lower entropy than uniform"
            
            # Test entropy bounds
            random_probs = np.random.dirichlet([1, 1, 1, 1])  # Random distribution
            random_entropy = shannon_entropy(random_probs)
            assert 0 <= random_entropy <= 2.0, "Entropy bounds violated"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))
    
    def test_conditional_entropy(self):
        """
        Test conditional entropy H(Y|X) calculation.
        
        MATHEMATICAL REQUIREMENTS:
        - H(Y|X) = Σₓ p(x) H(Y|X=x)
        - H(X,Y) = H(X) + H(Y|X) (chain rule)
        - H(Y|X) ≤ H(Y) (conditioning reduces entropy)
        - I(X;Y) = H(Y) - H(Y|X) (mutual information)
        """
        diagnostic = TestDiagnostic(
            component_name="Conditional Entropy Calculation",
            expected_behavior="Calculate conditional entropy and mutual information",
            failure_indicators=[
                "Conditional entropy calculation failed",
                "Chain rule validation incorrect",
                "Mutual information computation wrong",
                "Joint distribution handling failed"
            ],
            build_instructions=[
                "Add conditional_entropy function to info_entropy.py",
                "Implement joint distribution processing",
                "Add mutual information calculation",
                "Create chain rule validation",
                "Add information-theoretic bound checking"
            ],
            mathematical_requirements=[
                "H(Y|X) = -Σₓ,ᵧ p(x,y) log[p(y|x)]",
                "H(X,Y) = H(X) + H(Y|X) (chain rule)",
                "H(Y|X) ≤ H(Y) (conditioning property)",
                "I(X;Y) = H(X) + H(Y) - H(X,Y) ≥ 0"
            ],
            acceptance_criteria={
                "chain_rule": "H(X,Y) = H(X) + H(Y|X) within numerical precision",
                "conditioning_property": "H(Y|X) ≤ H(Y)",
                "mutual_info_positive": "I(X;Y) ≥ 0",
                "independence_zero": "I(X;Y) = 0 for independent X,Y"
            },
            physics_principle="Information theory: Conditioning cannot increase entropy"
        )
        
        # Framework for conditional entropy testing
        try:
            from math_utils.info_entropy import conditional_entropy, shannon_entropy

            # Case 1: Perfect correlation (Y = X)
            # H(Y|X) should be 0
            p_corr = np.array([[0.5, 0], [0, 0.5]])
            h_y_given_x_corr = conditional_entropy(p_corr)
            assert np.isclose(h_y_given_x_corr, 0), "H(Y|X) should be 0 for perfect correlation"

            # Case 2: Independence
            # H(Y|X) should be H(Y)
            p_ind = np.array([[0.25, 0.25], [0.25, 0.25]])
            p_y_ind = np.sum(p_ind, axis=0)
            h_y_ind = shannon_entropy(p_y_ind)
            h_y_given_x_ind = conditional_entropy(p_ind)
            assert np.isclose(h_y_given_x_ind, h_y_ind), "H(Y|X) should be H(Y) for independent vars"

            # Case 3: General case
            p_general = np.array([[0.4, 0.1], [0.2, 0.3]])
            p_x = np.sum(p_general, axis=1)
            p_y = np.sum(p_general, axis=0)
            h_x = shannon_entropy(p_x)
            h_y = shannon_entropy(p_y)
            h_xy = shannon_entropy(p_general.flatten())
            h_y_given_x = conditional_entropy(p_general)

            # Check chain rule: H(X,Y) = H(X) + H(Y|X)
            assert np.isclose(h_xy, h_x + h_y_given_x), "Chain rule H(X,Y) = H(X)+H(Y|X) violated"

            # Check conditioning property: H(Y|X) <= H(Y)
            assert h_y_given_x <= h_y, "Conditioning property H(Y|X) <= H(Y) violated"

        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))


class TestKolmogorovComplexity:
    """Test Kolmogorov complexity approximation methods."""
    
    def test_compression_based_approximation(self):
        """
        Test Kolmogorov complexity approximation via compression.
        
        MATHEMATICAL REQUIREMENTS:
        - K_approx(x) = min{|gzip(x)|, |bzip2(x)|, |lzma(x)|}
        - Bennett-Gács bound: |K(x) - K_approx(x)| ≤ c₁ log |x| + c₂ log log |x|
        - Monotonicity: more complex strings → higher K_approx
        - Compression universality for practical strings
        """
        diagnostic = TestDiagnostic(
            component_name="Kolmogorov Complexity Approximation",
            expected_behavior="Approximate Kolmogorov complexity using compression algorithms",
            failure_indicators=[
                "Compression algorithms not available",
                "K_approx calculation failed",
                "Bennett-Gács bounds violated", 
                "Monotonicity property broken"
            ],
            build_instructions=[
                "Add kolmogorov_approx function to info_entropy.py",
                "Integrate multiple compression algorithms (gzip, bzip2, lzma)",
                "Implement Bennett-Gács deviation bound validation",
                "Add monotonicity checking for complexity ordering",
                "Create compression algorithm selection and optimization"
            ],
            mathematical_requirements=[
                "K_approx(x) = min_algo |compress_algo(x)|",
                "|K(x) - K_approx(x)| ≤ c₁ log |x| + c₂ log log |x|",
                "K_approx(xy) ≤ K_approx(x) + K_approx(y) + O(log |xy|)",
                "K_approx(x) ≥ H(X) - O(log |x|) for source X"
            ],
            acceptance_criteria={
                "multi_compressor": "All compression algorithms working",
                "bounds_respected": "Bennett-Gács bounds satisfied",
                "monotonic_complexity": "Complex strings → higher K_approx",
                "compression_efficient": "Good approximation for typical code"
            },
            physics_principle="Algorithmic information theory: Complexity as shortest description length"
        )
        
        try:
            from math_utils.info_entropy import kolmogorov_approx

            # A highly repetitive string should have low complexity
            repetitive_string = "a" * 1000
            k_repetitive = kolmogorov_approx(repetitive_string)

            # A more random-looking string should have higher complexity
            random_string = "axbycz" * 167 # length is 1002
            k_random = kolmogorov_approx(random_string)

            # A string from a smaller alphabet should have lower complexity
            binary_string = "01" * 500 # length 1000
            k_binary = kolmogorov_approx(binary_string)

            # Test monotonicity
            assert k_repetitive < k_binary, "Repetitive string should be more compressible than binary"
            assert k_binary < k_random, "Binary string should be more compressible than random-like string"

            # Test that complexity is less than original length
            assert k_repetitive < len(repetitive_string.encode('utf-8'))
            assert k_random < len(random_string.encode('utf-8'))

        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))
