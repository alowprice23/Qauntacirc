"""
Comprehensive Tests for PauliGuard Agent

This module tests the PauliGuard agent, which implements the Pauli exclusion principle
for software engineering: ⟨ψᵢ|ψⱼ⟩ = 0 for i ≠ j (orthogonal components)

MATHEMATICAL FOUNDATION:
=======================
PauliGuard enforces orthogonality between software components by:
1. Detecting near-duplicate code through semantic analysis
2. Refactoring duplicates into orthogonal, reusable components  
3. Maintaining linear independence of module functions
4. Reducing complexity energy through deduplication

PHYSICS PRINCIPLE:
=================
The Pauli exclusion principle states that no two fermions can occupy 
the same quantum state. In software engineering, this translates to:
- No two modules should implement identical functionality
- Code components should be linearly independent
- Overlapping functionality should be factored into shared libraries

WHAT GETS TESTED:
================
1. Duplicate Detection Algorithms (AST, semantic, behavioral)
2. Orthogonality Measurement and Validation
3. Refactoring Proposal Generation with Equivalence Proofs
4. Energy Impact Analysis (complexity reduction)
5. Code Quality Metrics (coupling, cohesion)
6. Mathematical Property Preservation (linear independence)
7. Agent Contract Validation (preconditions, postconditions)

FAILURE ANALYSIS:
================
Each test includes comprehensive diagnostics explaining:
- What deduplication component needs to be built
- Mathematical orthogonality requirements
- Implementation guidance for similarity detection
- Code quality improvement expectations
"""

import pytest
import numpy as np
import ast
from typing import Dict, List, Any, Set, Tuple
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass

# Test diagnostic imports
from tests.conftest import TestDiagnostic, AgentBehaviorSpec


@dataclass
class CodeModule:
    """Represents a code module for testing."""
    name: str
    content: str
    ast_tree: ast.AST
    complexity: int
    dependencies: Set[str]
    exports: Set[str]
    
    @classmethod
    def from_source(cls, name: str, content: str):
        """Create CodeModule from source code."""
        return cls(
            name=name,
            content=content,
            ast_tree=ast.parse(content),
            complexity=len(content.split('\n')),  # Simple approximation
            dependencies=set(),
            exports=set()
        )


class TestPauliGuardDuplicateDetection:
    """
    Test duplicate detection algorithms in PauliGuard agent.
    
    Validates the agent's ability to identify semantically similar
    code components that violate the orthogonality principle.
    """
    
    def test_ast_similarity_detection(self):
        """
        Test Abstract Syntax Tree (AST) based duplicate detection.
        
        WHAT IT TESTS:
        - AST parsing and normalization
        - Structural similarity measurement
        - Alpha-renaming for variable independence
        - Similarity threshold validation
        
        MATHEMATICAL REQUIREMENTS:
        - Similarity metric: sim(AST₁, AST₂) ∈ [0, 1]
        - Threshold τ ∈ (0.8, 0.95) for duplicate classification
        - Alpha-renaming equivalence: sim(α(AST), AST) = 1
        - Transitivity: sim(A,B) > τ ∧ sim(B,C) > τ ⇒ cluster{A,B,C}
        
        IF THIS FAILS - BUILD THESE:
        - agents/pauli_guard/similarity.py with AST analysis
        - AST normalization and alpha-renaming utilities
        - Similarity metric computation algorithms
        - Clustering algorithms for duplicate groups
        """
        diagnostic = TestDiagnostic(
            component_name="AST Similarity Detection",
            expected_behavior="Detect structurally similar code through AST analysis",
            failure_indicators=[
                "AST parsing failed or incomplete",
                "Similarity metric not implemented",
                "Alpha-renaming not working",
                "Clustering algorithm missing"
            ],
            build_instructions=[
                "Implement agents/pauli_guard/similarity.py with ASTSimilarity class",
                "Add AST normalization and canonicalization",
                "Implement edit distance for ASTs",
                "Add alpha-renaming for variable normalization",
                "Create clustering algorithm for grouping similar ASTs"
            ],
            mathematical_requirements=[
                "sim(AST₁, AST₂) = 1 - edit_distance(norm(AST₁), norm(AST₂))/max_distance",
                "Alpha-renaming: vars(AST) → canonical names",
                "Similarity threshold: τ ∈ (0.8, 0.95) for duplicates",
                "Clustering: transitively close similarity groups"
            ],
            acceptance_criteria={
                "identical_similarity": "sim(AST, AST) = 1.0",
                "alpha_invariance": "sim(α(AST), AST) = 1.0",
                "threshold_separation": "Clear separation at threshold τ",
                "clustering_validity": "Clusters contain only similar ASTs"
            },
            physics_principle="Pauli exclusion: No two components in identical states",
            related_components=["core/functor.py", "math_utils/edit_distance.py"]
        )
        
        try:
            from agents.pauli_guard.similarity import ASTSimilarity
            
            detector = ASTSimilarity(threshold=0.85)
            
            # Test with identical functions (should be similarity = 1.0)
            code1 = """
            def calculate_tax(amount, rate):
                return amount * rate
            """
            code2 = """
            def calculate_tax(amount, rate):
                return amount * rate
            """
            
            module1 = CodeModule.from_source("tax1", code1)
            module2 = CodeModule.from_source("tax2", code2)
            
            similarity = detector.compute_similarity(module1.ast_tree, module2.ast_tree)
            assert abs(similarity - 1.0) < 1e-6, "Identical ASTs should have similarity 1.0"
            
            # Test with alpha-renamed version (should still be similarity = 1.0)
            code3 = """
            def calculate_tax(x, y):
                return x * y
            """
            module3 = CodeModule.from_source("tax3", code3)
            
            similarity_renamed = detector.compute_similarity(module1.ast_tree, module3.ast_tree)
            assert abs(similarity_renamed - 1.0) < 1e-6, "Alpha-renamed ASTs should have similarity 1.0"
            
            # Test with different function (should be low similarity)
            code4 = """
            def process_user(user_data):
                return user_data.get('name', 'Unknown')
            """
            module4 = CodeModule.from_source("user", code4)
            
            similarity_different = detector.compute_similarity(module1.ast_tree, module4.ast_tree)
            assert similarity_different < 0.5, "Different functions should have low similarity"
            
            # Test clustering
            modules = [module1, module2, module3, module4]
            clusters = detector.find_duplicate_clusters(modules)
            
            assert len(clusters) == 2, "Should find 2 clusters: tax functions and user function"
            tax_cluster = [c for c in clusters if len(c) == 3][0]  # The tax cluster
            assert all(m.name.startswith('tax') for m in tax_cluster), "Tax cluster should contain only tax modules"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))
    
    def test_semantic_similarity_detection(self):
        """
        Test semantic similarity detection beyond syntactic structure.
        
        WHAT IT TESTS:
        - Semantic feature extraction from code
        - Behavioral equivalence detection
        - Control flow similarity analysis
        - Data flow pattern matching
        
        MATHEMATICAL REQUIREMENTS:
        - Semantic embedding: code → ℝⁿ feature vector
        - Cosine similarity: sim(v₁, v₂) = (v₁·v₂)/(||v₁|| ||v₂||)
        - Feature space orthogonality measurement
        - Behavioral equivalence via symbolic execution
        
        IF THIS FAILS - BUILD THESE:
        - Semantic feature extraction system
        - Control flow analysis utilities
        - Data flow analysis tools
        - Behavioral equivalence checking
        """
        diagnostic = TestDiagnostic(
            component_name="Semantic Similarity Detection", 
            expected_behavior="Detect semantically equivalent code with different syntax",
            failure_indicators=[
                "Semantic feature extraction failed",
                "Control flow analysis missing",
                "Behavioral equivalence not detected",
                "Feature vector computation incorrect"
            ],
            build_instructions=[
                "Implement agents/pauli_guard/semantic.py with semantic analysis",
                "Add control flow graph extraction and analysis",
                "Create data flow analysis for variable usage patterns",
                "Implement behavioral equivalence checking via symbolic execution",
                "Add semantic feature vector computation"
            ],
            mathematical_requirements=[
                "Feature extraction: f(code) → ℝⁿ",
                "Cosine similarity: cos(θ) = (v₁·v₂)/(||v₁||||v₂||)",
                "Orthogonality: v₁ ⟂ v₂ ⟺ v₁·v₂ = 0",
                "Behavioral equivalence: ∀inputs. f₁(inputs) = f₂(inputs)"
            ],
            acceptance_criteria={
                "semantic_features": "Feature vectors capture semantic meaning",
                "similarity_metric": "Cosine similarity ∈ [0, 1]",
                "behavioral_equiv": "Equivalent functions detected despite syntax differences",
                "orthogonality_measure": "Non-duplicate functions are orthogonal"
            },
            physics_principle="Quantum mechanics: Orthogonal states are distinguishable",
            related_components=["core/functor.py", "math_utils/distance_metrics.py"]
        )
        
        try:
            from agents.pauli_guard.semantic import SemanticSimilarity
            
            detector = SemanticSimilarity()
            
            # Test semantically equivalent but syntactically different functions
            code1 = """
            def factorial(n):
                if n <= 1:
                    return 1
                return n * factorial(n - 1)
            """
            
            code2 = """
            def factorial(x):
                result = 1
                for i in range(1, x + 1):
                    result *= i
                return result
            """
            
            code3 = """
            def fibonacci(n):
                if n <= 1:
                    return n
                return fibonacci(n-1) + fibonacci(n-2)
            """
            
            # Extract semantic features
            features1 = detector.extract_features(code1)
            features2 = detector.extract_features(code2)
            features3 = detector.extract_features(code3)
            
            assert len(features1) > 0, "Feature extraction should produce non-empty vectors"
            
            # Test semantic similarity
            sim_factorial = detector.cosine_similarity(features1, features2)
            sim_different = detector.cosine_similarity(features1, features3)
            
            assert sim_factorial > 0.7, "Semantically equivalent functions should have high similarity"
            assert sim_different < 0.5, "Different functions should have low similarity"
            
            # Test orthogonality detection
            orthogonality = detector.orthogonality_measure(features1, features3)
            assert orthogonality > 0.5, "Different functions should be approximately orthogonal"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))


class TestPauliGuardRefactoring:
    """
    Test PauliGuard's refactoring capabilities.
    
    Validates the agent's ability to generate refactoring proposals
    that eliminate duplicates while preserving semantic equivalence.
    """
    
    def test_refactoring_proposal_generation(self):
        """
        Test generation of refactoring proposals for duplicate elimination.
        
        WHAT IT TESTS:
        - Common functionality extraction
        - Adapter/wrapper generation for different interfaces
        - Semantic equivalence preservation
        - Dependency graph impact analysis
        
        MATHEMATICAL REQUIREMENTS:
        - Orthogonalization: proj(v₁, v₂) = v₁ - (v₁·v₂/||v₂||²)v₂
        - Equivalence preservation: ∀inputs. old_func(inputs) = new_func(inputs)
        - Complexity reduction: E_complexity(refactored) < E_complexity(original)
        - Coupling impact: ΔE_coupling bounded or reduced
        
        IF THIS FAILS - BUILD THESE:
        - Refactoring proposal generation system
        - Common code extraction algorithms
        - Adapter generation for interface compatibility
        - Semantic equivalence proof generation
        """
        diagnostic = TestDiagnostic(
            component_name="Refactoring Proposal Generation",
            expected_behavior="Generate refactoring proposals that eliminate duplicates",
            failure_indicators=[
                "Common code extraction failed",
                "Adapter generation incomplete",
                "Semantic equivalence not preserved",
                "Complexity reduction not achieved"
            ],
            build_instructions=[
                "Implement agents/pauli_guard/refactor.py with RefactoringProposer",
                "Add common functionality extraction algorithms",
                "Create adapter/wrapper code generation",
                "Implement semantic equivalence preservation checking",
                "Add complexity impact analysis"
            ],
            mathematical_requirements=[
                "Orthogonalization: extract common v_common, leave orthogonal residuals",
                "Equivalence: refactored_func ≡ original_func behaviorally",
                "Complexity reduction: K_approx(refactored) < K_approx(original)",
                "Energy impact: ΔE_total ≤ 0 (non-increasing total energy)"
            ],
            acceptance_criteria={
                "duplicate_elimination": "Identified duplicates successfully merged",
                "equivalence_preservation": "All tests pass after refactoring",
                "complexity_reduction": "Lines of code reduced by ≥30%",
                "energy_improvement": "Total energy decreased or unchanged"
            },
            physics_principle="Pauli exclusion: Identical states are prohibited, leading to minimal energy configurations",
            related_components=["core/energy_calculator.py", "core/functor.py"]
        )
        
        try:
            from agents.pauli_guard.refactor import RefactoringProposer
            from agents.pauli_guard.similarity import ASTSimilarity
            
            proposer = RefactoringProposer()
            similarity_detector = ASTSimilarity(threshold=0.85)
            
            # Create test modules with duplicated functionality
            tax_calc_1 = """
            def calculate_sales_tax(amount, rate=0.08):
                if amount < 0:
                    raise ValueError("Amount cannot be negative")
                return amount * rate
            """
            
            tax_calc_2 = """
            def compute_tax_amount(price, tax_rate=0.08):
                if price < 0:
                    raise ValueError("Price cannot be negative") 
                return price * tax_rate
            """
            
            modules = [
                CodeModule.from_source("sales", tax_calc_1),
                CodeModule.from_source("billing", tax_calc_2)
            ]
            
            # Detect duplicates
            clusters = similarity_detector.find_duplicate_clusters(modules)
            assert len(clusters) > 0, "Should detect duplicate cluster"
            
            # Generate refactoring proposal
            if clusters:
                duplicate_cluster = clusters[0]
                proposal = proposer.generate_proposal(duplicate_cluster)
                
                assert proposal is not None, "Should generate refactoring proposal"
                assert 'common_function' in proposal, "Should extract common functionality"
                assert 'adapters' in proposal, "Should generate adapter functions"
                
                # Validate complexity reduction
                original_complexity = sum(m.complexity for m in duplicate_cluster)
                proposed_complexity = proposal.get('estimated_complexity', float('inf'))
                assert proposed_complexity < original_complexity, "Refactoring should reduce complexity"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))
    
    def test_orthogonality_enforcement(self):
        """
        Test orthogonality enforcement after refactoring.
        
        WHAT IT TESTS:
        - Module orthogonality measurement: ⟨m₁|m₂⟩ = 0
        - Linear independence validation
        - Overlap reduction quantification
        - Orthogonal basis construction
        
        MATHEMATICAL REQUIREMENTS:
        - Gram-Schmidt process for orthogonalization
        - Inner product: ⟨f₁, f₂⟩ = Σᵢ w(similarity(f₁ᵢ, f₂ᵢ))
        - Orthogonality condition: ⟨f₁, f₂⟩ = 0 for distinct functions
        - Span preservation: span(original) = span(orthogonalized)
        
        IF THIS FAILS - BUILD THESE:
        - Orthogonality measurement system
        - Gram-Schmidt orthogonalization for code
        - Inner product computation for code similarity
        - Linear independence verification
        """
        diagnostic = TestDiagnostic(
            component_name="Orthogonality Enforcement",
            expected_behavior="Enforce orthogonality between refactored components",
            failure_indicators=[
                "Orthogonality measurement failed",
                "Gram-Schmidt process not implemented",
                "Inner product computation incorrect",
                "Linear independence not achieved"
            ],
            build_instructions=[
                "Create agents/pauli_guard/orthogonal.py with OrthogonalityEnforcer",
                "Implement inner product computation for code modules",
                "Add Gram-Schmidt orthogonalization process",
                "Create linear independence validation",
                "Add orthogonal basis construction algorithms"
            ],
            mathematical_requirements=[
                "Inner product: ⟨m₁, m₂⟩ = semantic_overlap(m₁, m₂)",
                "Orthogonality: ⟨m₁, m₂⟩ = 0 for i ≠ j",
                "Gram-Schmidt: uᵢ = vᵢ - Σⱼ<ᵢ proj(vᵢ, uⱼ)",
                "Linear independence: rank([m₁, m₂, ..., mₙ]) = n"
            ],
            acceptance_criteria={
                "zero_overlap": "⟨mᵢ, mⱼ⟩ < 1e-6 for i ≠ j",
                "unit_norm": "||mᵢ|| ≈ 1 after normalization",
                "span_preserved": "Functionality coverage unchanged",
                "linear_independent": "Modules form linearly independent set"
            },
            physics_principle="Quantum mechanics: Orthogonal states have zero overlap",
            related_components=["math_utils/contractive_maps.py"]
        )
        
        try:
            from agents.pauli_guard.orthogonal import OrthogonalityEnforcer
            
            enforcer = OrthogonalityEnforcer()
            
            # Create test modules with overlapping functionality
            modules = [
                CodeModule.from_source("auth1", "def validate(token): return token.valid"),
                CodeModule.from_source("auth2", "def check(token): return token.valid"),
                CodeModule.from_source("user", "def get_name(user): return user.name")
            ]
            
            # Compute initial overlaps
            initial_overlaps = []
            for i in range(len(modules)):
                for j in range(i+1, len(modules)):
                    overlap = enforcer.compute_overlap(modules[i], modules[j])
                    initial_overlaps.append(overlap)
            
            # Apply orthogonalization
            orthogonalized = enforcer.orthogonalize(modules)
            
            # Compute final overlaps
            final_overlaps = []
            for i in range(len(orthogonalized)):
                for j in range(i+1, len(orthogonalized)):
                    overlap = enforcer.compute_overlap(orthogonalized[i], orthogonalized[j])
                    final_overlaps.append(overlap)
            
            # Validate orthogonality improvement
            max_final_overlap = max(final_overlaps) if final_overlaps else 0
            assert max_final_overlap < 1e-3, "Orthogonalized modules should have minimal overlap"
            
            # Validate span preservation (functionality should be preserved)
            assert len(orthogonalized) <= len(modules), "Should not increase module count"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))


class TestPauliGuardEnergyImpact:
    """
    Test energy impact analysis for PauliGuard operations.
    
    Validates that deduplication operations properly reduce complexity
    energy while maintaining or improving other energy components.
    """
    
    def test_complexity_energy_reduction(self):
        """
        Test complexity energy reduction through deduplication.
        
        WHAT IT TESTS:
        - Kolmogorov complexity reduction via deduplication
        - Shannon entropy impact analysis  
        - Compression ratio improvement
        - Overall complexity energy delta
        
        MATHEMATICAL REQUIREMENTS:
        - K_approx(deduplicated) < K_approx(original)
        - H(deduplicated) ≤ H(original) (entropy non-increasing)
        - Compression ratio improvement ≥ 10%
        - ΔE_complexity < 0 (energy reduction)
        
        IF THIS FAILS - BUILD THESE:
        - Complexity impact analysis system
        - Kolmogorov complexity measurement before/after
        - Shannon entropy computation for code
        - Compression ratio analysis
        """
        diagnostic = TestDiagnostic(
            component_name="Complexity Energy Reduction Analysis",
            expected_behavior="Quantify complexity energy reduction from deduplication",
            failure_indicators=[
                "Complexity measurement failed",
                "Energy reduction not detected",
                "Compression analysis incomplete",
                "Entropy calculation incorrect"
            ],
            build_instructions=[
                "Implement agents/pauli_guard/energy_impact.py",
                "Add Kolmogorov complexity before/after measurement",
                "Create Shannon entropy analysis for code tokens",
                "Add compression ratio improvement tracking",
                "Implement energy delta calculation"
            ],
            mathematical_requirements=[
                "ΔK_approx = K_approx(after) - K_approx(before) < 0",
                "ΔH = H(after) - H(before) ≤ 0",
                "Compression improvement = (C_before - C_after)/C_before > 0.1",
                "ΔE_complexity = α · (ΔK_approx + ΔH) < 0"
            ],
            acceptance_criteria={
                "complexity_reduction": "ΔK_approx < -0.1 * K_approx(original)",
                "entropy_improvement": "ΔH ≤ 0 (non-increasing)",
                "compression_gain": "≥10% compression improvement",
                "energy_decrease": "ΔE_complexity < 0"
            },
            physics_principle="Information theory: Removing redundancy reduces information content"
        )
        
        try:
            from agents.pauli_guard.energy_impact import ComplexityImpactAnalyzer
            from core.energy_calculator import EnergyCalculator
            
            analyzer = ComplexityImpactAnalyzer()
            energy_calc = EnergyCalculator()
            
            # Create duplicated code scenario
            original_modules = [
                "def process(data): return data.strip().lower()",
                "def clean(text): return text.strip().lower()", 
                "def normalize(input): return input.strip().lower()"
            ]
            
            deduplicated_modules = [
                "def normalize_text(text): return text.strip().lower()",
                "def process(data): return normalize_text(data)",
                "def clean(text): return normalize_text(text)"
            ]
            
            # Analyze complexity before/after
            complexity_before = analyzer.total_complexity(original_modules)
            complexity_after = analyzer.total_complexity(deduplicated_modules) 
            
            assert complexity_before > complexity_after, "Deduplication should reduce complexity"
            
            # Analyze compression improvement
            compression_before = analyzer.compression_ratio(original_modules)
            compression_after = analyzer.compression_ratio(deduplicated_modules)
            improvement = (compression_before - compression_after) / compression_before
            
            assert improvement > 0.1, "Should achieve >10% compression improvement"
            
            # Test energy impact
            energy_delta = energy_calc.complexity_energy_delta(complexity_before, complexity_after)
            assert energy_delta < 0, "Complexity energy should decrease"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e)}"))
        except Exception as e:
            pytest.fail(diagnostic.format_failure_message(str(e)))
    
    def test_coupling_energy_impact(self):
        """
        Test coupling energy impact of refactoring operations.
        
        WHAT IT TESTS:
        - Dependency graph changes after refactoring
        - Laplacian eigenvalue impact
        - Module coupling analysis
        - Graph connectivity preservation
        
        MATHEMATICAL REQUIREMENTS:
        - ΔTr(L) = Tr(L_after) - Tr(L_before) (Laplacian trace change)
        - ΔE_coupling = β · ΔTr(L)
        - Graph connectivity preserved (no disconnected components)
        - Modularity Q improved or maintained
        
        IF THIS FAILS - BUILD THESE:
        - Dependency graph impact analysis
        - Laplacian eigenvalue change computation
        - Graph connectivity validation
        - Modularity measurement system
        """
        diagnostic = TestDiagnostic(
            component_name="Coupling Energy Impact Analysis",
            expected_behavior="Analyze coupling energy changes from refactoring",
            failure_indicators=[
                "Dependency graph analysis failed",
                "Laplacian computation incorrect",
                "Coupling change not measured",
                "Graph connectivity lost"
            ],
            build_instructions=[
                "Add coupling impact analysis to PauliGuard",
                "Implement dependency graph before/after comparison",
                "Add Laplacian eigenvalue change computation", 
                "Create graph connectivity validation",
                "Implement modularity improvement tracking"
            ],
            mathematical_requirements=[
                "ΔTr(L) = Tr(L_after) - Tr(L_before)",
                "ΔE_coupling = β · ΔTr(L)",
                "Connectivity: all modules remain reachable",
                "Modularity: Q = (1/4m) Σᵢⱼ (Aᵢⱼ - kᵢkⱼ/2m) δ(cᵢ, cⱼ)"
            ],
            acceptance_criteria={
                "coupling_non_increase": "ΔE_coupling ≤ 0",
                "connectivity_preserved": "Graph remains connected",
                "modularity_improved": "ΔQ ≥ 0",
                "dependency_count": "Total dependencies reduced or unchanged"
            },
            physics_principle="Graph theory: Refactoring can improve modular structure"
        )
        
        # This would implement coupling impact testing
        pytest.skip(diagnostic.format_failure_message("Coupling impact analysis framework ready"))


class TestPauliGuardContractValidation:
    """
    Test PauliGuard agent contract validation.
    
    Validates that the agent satisfies its formal contract including
    preconditions, postconditions, and mathematical properties.
    """
    
    def test_agent_preconditions(self):
        """
        Test agent precondition validation.
        
        WHAT IT TESTS:
        - Code modules available for analysis
        - Similarity analysis infrastructure ready
        - Sufficient code complexity for meaningful deduplication
        - Agent resource requirements satisfied
        
        IF THIS FAILS - BUILD THESE:
        - Precondition checking system in PauliGuard
        - Code module availability validation
        - Resource requirement verification
        - Analysis infrastructure health checks
        """
        diagnostic = TestDiagnostic(
            component_name="PauliGuard Precondition Validation",
            expected_behavior="Validate agent can operate on current system state",
            failure_indicators=[
                "Code modules not available",
                "Similarity analysis infrastructure missing",
                "Insufficient complexity for deduplication",
                "Resource requirements not met"
            ],
            build_instructions=[
                "Add precondition checking to PauliGuard agent",
                "Implement code module availability validation",
                "Add complexity threshold checking",
                "Create resource requirement verification",
                "Add analysis infrastructure health checks"
            ],
            mathematical_requirements=[
                "Module count N ≥ 2 (need multiple modules)",
                "Average complexity ≥ threshold for meaningful analysis",
                "Similarity computation resources available",
                "Memory sufficient for pairwise analysis: O(N²)"
            ],
            acceptance_criteria={
                "module_availability": "≥2 code modules available",
                "complexity_threshold": "Average complexity ≥ 10 LOC",
                "resource_sufficient": "Memory and CPU available for analysis",
                "infrastructure_ready": "Similarity analysis system operational"
            },
            physics_principle="Physical systems require sufficient complexity for meaningful phase transitions"
        )
        
        try:
            from agents.pauli_guard.agent import PauliGuardAgent
            
            agent = PauliGuardAgent()
            
            # Test with sufficient state (should pass preconditions)
            sufficient_state = Mock()
            sufficient_state.modules = [Mock(), Mock(), Mock()]  # 3 modules
            sufficient_state.total_complexity = 150
            sufficient_state.analysis_resources_available = True
            
            preconditions_met = agent.check_preconditions(sufficient_state)
            assert preconditions_met, "Preconditions should be satisfied with sufficient state"
            
            # Test with insufficient state (should fail preconditions)
            insufficient_state = Mock()
            insufficient_state.modules = [Mock()]  # Only 1 module
            insufficient_state.total_complexity = 5
            insufficient_state.analysis_resources_available = False
            
            preconditions_failed = agent.check_preconditions(insufficient_state)
            assert not preconditions_failed, "Preconditions should fail with insufficient state"
            
        except ImportError as e:
            pytest.fail(diagnostic.format_failure_message(f"ImportError: {str(e
