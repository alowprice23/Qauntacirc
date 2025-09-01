# Plan for the `core` Directory (v4 - Exhaustive & Comprehensive)

## 1. Guiding Philosophy & Core Principles

The `core` directory is the mathematical and logical heart of the QuantaCirc system. It is where the abstract principles of physics-grounded software engineering are made concrete, computable, and verifiable. It does not contain agent-specific logic or user-facing commands; instead, it provides the foundational engine upon which the entire agentic system operates. Every module in this directory is a direct implementation of a concept from our foundational "QuantaCirc Series" documentation.

1.  **Mathematical Rigor as Code**: The functions and classes within `core` are direct translations of the mathematical formulas and theorems that define QuantaCirc. For example, `core/energy_calculator.py` implements the `E_approx` function, and `core/two_phase_annealer.py` implements the optimization algorithm proven to converge on its minimum. This directly reflects the principle of building a system on an irrefutable logical foundation.

2.  **Computable and Verifiable**: Every function must be deterministic and produce verifiable artifacts. There is no room for heuristics or ambiguity here. The outputs are not just data, but proofs, certificates, and measurable bounds that feed into the system's "irrefutability" claim, as detailed in the `Readme.md`.

3.  **Decoupled Engine**: The core is an engine that is driven by an external orchestrator (which also lives in `core` but acts as an interface). It knows nothing of specific agents like `PlanckForge` or `PauliGuard` directly. It only knows about the mathematical state `S`, the energy `E`, and the transformations that are proven to be safe and contract-abiding. This modularity is key to the system's scalability and maintainability.

4.  **State as a First-Class Citizen**: The representation of the software state (`S`), its quantum mechanical analogue (`ρ`), and the metrics (`Φ`, `λ`) are precisely defined in Pydantic models (`core/types.py`) and managed with absolute consistency. This ensures that the system always operates on a well-defined, verifiable state.

5.  **Performance with Correctness**: While correctness, guaranteed by theorems, is the primary concern, the core numerical routines must be performant enough to enable an interactive development loop. This implies careful use of libraries like `numpy` and `scipy` and building in mechanisms for incremental computation and caching.

---

## 2. File-by-File Implementation Plan

This section provides an exhaustive plan for every file within the `core` directory, as specified in the 420-file lean-agentic map.

---

### **File: `core/__init__.py`**
*   **Purpose**: To define the public API of the `core` package, making it a well-structured Python package. It will explicitly export the key classes and functions that other parts of the system (like the CLI and agents) are allowed to interact with. This enforces a clean separation of concerns and prevents other parts of the system from depending on internal implementation details of the `core` package.
*   **Est. LOC**: 25
*   **Dependencies**: None.
*   **Internal Imports/Relationships**:
    *   `from .orchestrator import Orchestrator`
    *   `from .energy_calculator import EnergyCalculator`
    *   `from .functor import Functor`
    *   `from .run_ledger import RunLedger`
    *   `from .types import QCState, QCEnergy`
    *   `from .constraint_solver import ConstraintSolver`
    *   `from .lyapunov_monitor import LyapunovMonitor`
*   **Implementation Details**:
    *   The file will contain a `__all__` list that explicitly enumerates the public interface of the `core` package. This is a critical aspect of maintaining a clean architecture.
    ```python
    # core/__init__.py
    __all__ = [
        "Orchestrator",
        "EnergyCalculator",
        "Functor",
        "RunLedger",
        "ConstraintSolver",
        "LyapunovMonitor",
        "QCState",
        "QCEnergy",
    ]
    ```
*   **Potential Issues**: Circular dependencies are a potential risk if modules within `core` attempt to import from this `__init__.py`. The development process must enforce a strict rule that all internal imports within the `core` package are direct (e.g., `from . import types`) to avoid this common architectural pitfall.

---

### **File: `core/orchestrator.py`**
*   **Purpose**: This is the central control loop of the entire QuantaCirc system. It embodies the agentic architecture, orchestrating the ten specialized agents based on the system's current state (`S`), energy (`E_approx`), and the overall goal. It ensures that the system evolves in a controlled, convergent, and verifiable manner, directly reflecting the "perfect closed loop" concept from the `Readme.md`.
*   **Est. LOC**: 500
*   **Dependencies**: `asyncio`, `pydantic`.
*   **Internal Imports/Relationships**: This is the primary consumer of almost all other `core` modules.
    *   `core.run_ledger`: To log every single action, decision, and state change for auditability.
    *   `core/energy_calculator.py`, `core/lyapunov_monitor.py`: To evaluate the state `S_t` at each step `t` and make decisions based on `E_approx` and `Φ`.
    *   `core/two_phase_annealer.py`: To get the annealing schedule (`T_k`) and acceptance probabilities.
    *   `core/convergence_engine.py`: To determine when to switch from Phase A to Phase B and when the system has reached a fixed point.
    *   `messaging.nats_client`: To communicate asynchronously with the agent services.
*   **Implementation Details**:
    1.  **State Machine**: Implemented as an `Orchestrator` class with a state machine. The states will be `IDLE`, `PLANNING`, `GENERATING`, `VERIFYING`, `CONVERGED`, `HALTED`.
    2.  **Main Loop**: An `async def run(self):` method will contain the main event loop, consuming tasks from a NATS topic.
    3.  **Agent Communication**: It will publish `AgentTask` messages and subscribe to `AgentResult` topics, ensuring agents are decoupled.
    4.  **Gate Stack**: A critical method `_apply_gate_stack(proposal)` will be implemented. This method will sequentially check a proposed change against all system invariants before it is accepted.
*   **Potential Issues**:
    *   **Deadlock/Livelock**: The orchestrator must have robust timeout and retry mechanisms to prevent getting stuck waiting for an agent or looping on a failing proposal. The `LyapunovMonitor` will be a key component in detecting and breaking these loops.

---

### **File: `core/run_ledger.py`**
*   **Purpose**: Implements the auditable log of all system runs, decisions, and artifacts. This is the system's "memory" and provides complete traceability for debugging, compliance, and learning. Every action taken by the orchestrator and agents is recorded here with cryptographic integrity.
*   **Est. LOC**: 200
*   **Dependencies**: `sqlite3`, `hashlib`, `json`, `datetime`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Uses `RunRecord`, `AgentTask`, `AgentResult` data structures.
    *   `core/serialization.py`: For consistent serialization of complex objects.
*   **Implementation Details**:
    1.  **Database Schema**: SQLite database with tables for `runs`, `decisions`, `artifacts`, `agent_actions`.
    2.  **Cryptographic Integrity**: Each record includes SHA-256 hash of previous record, creating blockchain-like integrity chain.
    3.  **Query Interface**: Rich query capabilities for analytics and debugging.
    ```python
    class RunLedger:
        def record_run_start(self, run_id: str, initial_state: QCState) -> None
        def record_agent_action(self, agent_name: str, task: AgentTask, result: AgentResult) -> None
        def record_state_transition(self, from_state: QCState, to_state: QCState, energy_delta: float) -> None
        def get_run_history(self, run_id: str) -> List[RunRecord]
        def query_similar_decisions(self, current_state: QCState) -> List[HistoricalDecision]
    ```
*   **Potential Issues**:
    *   **Performance**: Large ledgers could impact query performance. Implement indexing and archival strategies.
    *   **Concurrency**: Multiple agents writing simultaneously requires careful locking mechanisms.

---

### **File: `core/energy_calculator.py`**
*   **Purpose**: Implements the core energy function `E_approx = E_static + E_dynamic + E_interaction` that drives the entire optimization process. This is the mathematical heart of the quantum-mechanical approach to software engineering.
*   **Est. LOC**: 350
*   **Dependencies**: `numpy`, `scipy`, `typing`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Uses `QCState`, `EnergyComponents`, `SystemMetrics`.
    *   `core/state_space.py`: For computing state distances and transformations.
    *   `math/`: Various mathematical utilities for computing energy components.
*   **Implementation Details**:
    1.  **Energy Components**:
        *   `E_static`: Code complexity, coupling, cohesion metrics
        *   `E_dynamic`: Runtime performance, memory usage, I/O patterns
        *   `E_interaction`: Inter-module dependencies, API surface areas
    2.  **Incremental Computation**: Efficient recomputation when state changes locally.
    3.  **Caching Strategy**: LRU cache for expensive computations with cache invalidation.
    ```python
    class EnergyCalculator:
        def compute_total_energy(self, state: QCState) -> float
        def compute_static_energy(self, state: QCState) -> float
        def compute_dynamic_energy(self, state: QCState) -> float
        def compute_interaction_energy(self, state: QCState) -> float
        def energy_gradient(self, state: QCState) -> np.ndarray
        def energy_hessian(self, state: QCState) -> np.ndarray
    ```
*   **Potential Issues**:
    *   **Computational Complexity**: Energy computation must be efficient enough for interactive use.
    *   **Numerical Stability**: Ensure energy function is well-conditioned and numerically stable.

---

### **File: `core/closure_rules.py`**
*   **Purpose**: Manages and applies the Δ closure rule set that ensures system consistency and prevents invalid state transitions. This enforces the "irrefutability" guarantee by checking all proposed changes against formal constraints.
*   **Est. LOC**: 150
*   **Dependencies**: `typing`, `abc`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Uses `ClosureRule`, `StateTransition`, `ValidationResult`.
    *   `core/constraint_solver.py`: For complex constraint checking via SMT solving.
*   **Implementation Details**:
    1.  **Rule Engine**: Pluggable rule system with built-in and custom rules.
    2.  **Validation Pipeline**: Sequential rule application with short-circuit evaluation.
    3.  **Rule Categories**: Type safety, dependency consistency, mathematical constraints.
    ```python
    class ClosureRuleSet:
        def add_rule(self, rule: ClosureRule) -> None
        def validate_transition(self, from_state: QCState, to_state: QCState) -> ValidationResult
        def get_violated_rules(self, transition: StateTransition) -> List[ClosureRule]
        def suggest_fixes(self, violations: List[RuleViolation]) -> List[FixSuggestion]
    ```

---

### **File: `core/convergence_engine.py`**
*   **Purpose**: Detects convergence conditions (λ < 1, gradient norms) and manages phase transitions between exploration (Phase A) and exploitation (Phase B) in the two-phase annealing algorithm.
*   **Est. LOC**: 250
*   **Dependencies**: `numpy`, `scipy`.
*   **Internal Imports/Relationships**:
    *   `core/energy_calculator.py`: For computing energy gradients and monitoring convergence.
    *   `core/lyapunov_monitor.py`: For Lyapunov potential-based convergence detection.
    *   `math/`: Mathematical utilities for convergence analysis.
*   **Implementation Details**:
    1.  **Convergence Criteria**: Multiple convergence tests (energy, gradient, Lyapunov).
    2.  **Phase Management**: State machine for Phase A/B transitions.
    3.  **Adaptive Thresholds**: Dynamic adjustment of convergence thresholds.
    ```python
    class ConvergenceEngine:
        def check_convergence(self, state_history: List[QCState]) -> ConvergenceResult
        def should_switch_phase(self, current_phase: str, metrics: SystemMetrics) -> bool
        def estimate_contraction_factor(self, state_sequence: List[QCState]) -> float
        def predict_convergence_time(self, current_state: QCState) -> Optional[float]
    ```

---

### **File: `core/two_phase_annealer.py`**
*   **Purpose**: Implements the two-phase annealing optimization algorithm proven to converge to the global minimum. This provides the mathematical foundation for the entire optimization process.
*   **Est. LOC**: 300
*   **Dependencies**: `numpy`, `scipy`, `random`.
*   **Internal Imports/Relationships**:
    *   `core/energy_calculator.py`: For energy evaluation during optimization.
    *   `core/convergence_engine.py`: For phase transition decisions.
    *   `math/annealing.py`: Mathematical utilities for simulated annealing.
*   **Implementation Details**:
    1.  **Phase A (Exploration)**: High temperature, broad search, diverse proposals.
    2.  **Phase B (Exploitation)**: Low temperature, local search, refinement.
    3.  **Temperature Schedule**: Adaptive cooling schedule based on acceptance rates.
    4.  **Proposal Generation**: State-aware proposal mechanisms for efficient search.
    ```python
    class TwoPhaseAnnealer:
        def __init__(self, energy_calculator: EnergyCalculator, convergence_engine: ConvergenceEngine)
        def anneal(self, initial_state: QCState, max_iterations: int) -> AnnealingResult
        def phase_a_step(self, current_state: QCState, temperature: float) -> QCState
        def phase_b_step(self, current_state: QCState, temperature: float) -> QCState
        def acceptance_probability(self, energy_delta: float, temperature: float) -> float
    ```

---

### **File: `core/functor.py`**
*   **Purpose**: Implements the SoftSys -> QuantSys functor (ρ computation) that maps software engineering concepts to quantum mechanical analogues. This is the theoretical bridge that enables quantum-mechanical reasoning about software.
*   **Est. LOC**: 300
*   **Dependencies**: `numpy`, `scipy`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Uses `SoftwareState`, `QuantumState`, `FunctorMapping`.
    *   `math/`: Quantum mechanical utilities and linear algebra operations.
*   **Implementation Details**:
    1.  **State Mapping**: Converts software artifacts to quantum state representations.
    2.  **Observable Computation**: Maps software metrics to quantum observables.
    3.  **Unitary Evolution**: Models software transformations as unitary operations.
    ```python
    class Functor:
        def map_software_to_quantum(self, soft_state: SoftwareState) -> QuantumState
        def compute_density_matrix(self, soft_state: SoftwareState) -> np.ndarray
        def evolve_quantum_state(self, quantum_state: QuantumState, transformation: UnitaryOp) -> QuantumState
        def measure_observable(self, quantum_state: QuantumState, observable: Observable) -> float
    ```

---

### **File: `core/constraint_solver.py`**
*   **Purpose**: SMT (Satisfiability Modulo Theories) solver front-end for checking constraint violations and ensuring system consistency. Provides formal verification capabilities for the closure rules.
*   **Est. LOC**: 180
*   **Dependencies**: `z3-solver`, `typing`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Uses `Constraint`, `SMTResult`, `ProofCertificate`.
    *   `core/closure_rules.py`: For translating closure rules to SMT constraints.
*   **Implementation Details**:
    1.  **Constraint Translation**: Converts Python constraints to Z3 formulas.
    2.  **Incremental Solving**: Efficient constraint solving with incremental updates.
    3.  **Proof Extraction**: Extracts unsatisfiable cores and proof certificates.
    ```python
    class ConstraintSolver:
        def add_constraint(self, constraint: Constraint) -> None
        def check_satisfiability(self) -> SMTResult
        def get_model(self) -> Optional[Dict[str, Any]]
        def get_unsat_core(self) -> List[Constraint]
        def generate_proof_certificate(self) -> ProofCertificate
    ```

---

### **File: `core/error_budget.py`**
*   **Purpose**: Manages the project's error budget and risk calculations, implementing the economic model of software quality where errors have costs and verification has benefits.
*   **Est. LOC**: 200
*   **Dependencies**: `typing`, `dataclasses`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Uses `ErrorBudget`, `RiskAssessment`, `QualityMetrics`.
    *   `core/metrics.py`: For collecting quality and reliability metrics.
*   **Implementation Details**:
    1.  **Budget Allocation**: Distributes error budget across system components.
    2.  **Risk Calculation**: Probabilistic risk assessment based on historical data.
    3.  **Adaptive Budgeting**: Dynamic budget adjustment based on system evolution.
    ```python
    class ErrorBudgetManager:
        def allocate_budget(self, components: List[Component], total_budget: float) -> BudgetAllocation
        def consume_budget(self, component: Component, error_cost: float) -> BudgetStatus
        def assess_risk(self, current_state: QCState) -> RiskAssessment
        def recommend_actions(self, budget_status: BudgetStatus) -> List[Action]
    ```

---

### **File: `core/lyapunov_monitor.py`**
*   **Purpose**: Tracks the Φ Lyapunov function and bounded excursions to ensure system stability and convergence. This provides mathematical guarantees about system behavior.
*   **Est. LOC**: 220
*   **Dependencies**: `numpy`, `scipy`.
*   **Internal Imports/Relationships**:
    *   `core/energy_calculator.py`: For computing energy-based Lyapunov candidates.
    *   `math/lyapunov.py`: Mathematical utilities for Lyapunov analysis.
*   **Implementation Details**:
    1.  **Lyapunov Function**: Computes Φ(S_t) for system state S_t.
    2.  **Stability Analysis**: Monitors bounded excursions and convergence properties.
    3.  **Martingale Properties**: Ensures supermartingale convergence conditions.
    ```python
    class LyapunovMonitor:
        def compute_lyapunov_function(self, state: QCState) -> float
        def track_excursion(self, state_sequence: List[QCState]) -> ExcursionAnalysis
        def verify_stability(self, state_history: List[QCState]) -> StabilityResult
        def predict_convergence(self, current_state: QCState) -> ConvergencePrediction
    ```

---

### **File: `core/state_space.py`**
*   **Purpose**: Defines the software state space S and its transformations, providing the mathematical framework for representing and manipulating software system states.
*   **Est. LOC**: 150
*   **Dependencies**: `typing`, `abc`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Uses `QCState`, `StateTransformation`, `StateMetrics`.
    *   `core/edit_distance.py`: For computing distances between states.
*   **Implementation Details**:
    1.  **State Representation**: Structured representation of software system state.
    2.  **Transformation Algebra**: Mathematical operations on state transformations.
    3.  **State Metrics**: Distance functions and similarity measures.
    ```python
    class StateSpace:
        def create_state(self, **kwargs) -> QCState
        def apply_transformation(self, state: QCState, transformation: StateTransformation) -> QCState
        def compute_distance(self, state1: QCState, state2: QCState) -> float
        def find_neighbors(self, state: QCState, radius: float) -> List[QCState]
    ```

---

### **File: `core/edit_distance.py`**
*   **Purpose**: Computes various distance metrics between software states, enabling quantitative comparison and similarity analysis for optimization and learning.
*   **Est. LOC**: 80
*   **Dependencies**: `numpy`, `typing`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Uses `QCState`, `DistanceMetric`.
*   **Implementation Details**:
    1.  **Multiple Metrics**: Hamming, Levenshtein, structural distances.
    2.  **Efficient Computation**: Optimized algorithms for large state spaces.
    3.  **Metric Properties**: Ensures triangle inequality and other metric axioms.
    ```python
    def hamming_distance(state1: QCState, state2: QCState) -> float
    def levenshtein_distance(state1: QCState, state2: QCState) -> float
    def structural_distance(state1: QCState, state2: QCState) -> float
    def semantic_distance(state1: QCState, state2: QCState) -> float
    ```

---

### **File: `core/metrics.py`**
*   **Purpose**: Core metrics emitters for the system, providing comprehensive observability into system behavior, performance, and mathematical properties.
*   **Est. LOC**: 100
*   **Dependencies**: `prometheus_client`, `typing`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Uses `MetricDefinition`, `MetricValue`.
    *   `monitoring/metrics.py`: For metrics collection infrastructure.
*   **Implementation Details**:
    1.  **Metric Types**: Counters, gauges, histograms, summaries for different metric types.
    2.  **Mathematical Metrics**: Energy, Lyapunov, convergence rate metrics.
    3.  **Performance Metrics**: Execution time, memory usage, throughput metrics.
    ```python
    class CoreMetrics:
        def emit_energy_metric(self, energy: float, components: Dict[str, float]) -> None
        def emit_convergence_metric(self, iteration: int, lambda_value: float) -> None
        def emit_performance_metric(self, operation: str, duration: float) -> None
        def emit_stability_metric(self, lyapunov_value: float) -> None
    ```

---

### **File: `core/validators.py`**
*   **Purpose**: Core validation functions for system integrity, ensuring that all data structures and operations maintain consistency and correctness.
*   **Est. LOC**: 120
*   **Dependencies**: `pydantic`, `typing`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Validates all core data structures.
    *   `core/exceptions.py`: For raising validation-specific exceptions.
*   **Implementation Details**:
    1.  **Schema Validation**: Pydantic-based validation for all data structures.
    2.  **Business Logic Validation**: Domain-specific validation rules.
    3.  **Cross-Reference Validation**: Ensures consistency across related objects.
    ```python
    class CoreValidators:
        def validate_state(self, state: QCState) -> ValidationResult
        def validate_energy_components(self, components: EnergyComponents) -> ValidationResult
        def validate_transformation(self, transformation: StateTransformation) -> ValidationResult
        def validate_constraints(self, constraints: List[Constraint]) -> ValidationResult
    ```

---

### **File: `core/exceptions.py`**
*   **Purpose**: Custom exception types for the core system, providing structured error information with context, correlation IDs, and suggested fixes.
*   **Est. LOC**: 70
*   **Dependencies**: `typing`, `uuid`.
*   **Internal Imports/Relationships**: None (base exception definitions).
*   **Implementation Details**:
    1.  **Exception Hierarchy**: Structured exception types for different error categories.
    2.  **Context Information**: Rich context including correlation IDs and stack traces.
    3.  **Suggested Fixes**: Machine-readable suggested fixes for common errors.
    ```python
    class QuantaCircError(Exception):
        def __init__(self, message: str, correlation_id: str = None, suggested_fix: str = None)
    
    class EnergyCalculationError(QuantaCircError): pass
    class ConvergenceError(QuantaCircError): pass
    class StateValidationError(QuantaCircError): pass
    class ConstraintViolationError(QuantaCircError): pass
    ```

---

### **File: `core/types.py`**
*   **Purpose**: Core Pydantic models and type definitions that form the data architecture backbone of the entire system. Every data structure used across the system is defined here.
*   **Est. LOC**: 180
*   **Dependencies**: `pydantic`, `typing`, `datetime`, `uuid`.
*   **Internal Imports/Relationships**: Used by virtually every other module in the system.
*   **Implementation Details**:
    1.  **State Models**: `QCState`, `SoftwareState`, `QuantumState` definitions.
    2.  **Energy Models**: `EnergyComponents`, `EnergyResult` with validation.
    3.  **Agent Models**: `AgentTask`, `AgentResult`, `AgentStatus` for agent communication.
    4.  **Mathematical Models**: `LyapunovResult`, `ConvergenceMetrics`, `OptimizationResult`.
    ```python
    class QCState(BaseModel):
        id: UUID
        timestamp: datetime
        software_state: SoftwareState
        quantum_state: Optional[QuantumState]
        energy: float
        metadata: Dict[str, Any]
    
    class EnergyComponents(BaseModel):
        static: float
        dynamic: float
        interaction: float
        total: float = Field(..., description="Sum of all components")
    ```

---

### **File: `core/serialization.py`**
*   **Purpose**: Serialization and deserialization of core data structures with versioning, compression, and integrity checking for persistence and communication.
*   **Est. LOC**: 100
*   **Dependencies**: `pickle`, `json`, `gzip`, `hashlib`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Serializes all core data structures.
*   **Implementation Details**:
    1.  **Multiple Formats**: JSON, Pickle, MessagePack support.
    2.  **Version Management**: Schema versioning for backward compatibility.
    3.  **Integrity Checking**: Checksums and signature verification.
    ```python
    class Serializer:
        def serialize_state(self, state: QCState, format: str = "json") -> bytes
        def deserialize_state(self, data: bytes, format: str = "json") -> QCState
        def serialize_with_compression(self, obj: Any) -> bytes
        def verify_integrity(self, data: bytes, checksum: str) -> bool
    ```

---

### **File: `core/persistence.py`**
*   **Purpose**: Handles persistence of system state with atomic operations, transactions, and recovery mechanisms to ensure data consistency and durability.
*   **Est. LOC**: 130
*   **Dependencies**: `sqlite3`, `typing`, `pathlib`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Persists core data structures.
    *   `core/serialization.py`: For data serialization before storage.
*   **Implementation Details**:
    1.  **Atomic Operations**: ACID transactions for state changes.
    2.  **Snapshot Management**: Efficient state snapshots with incremental updates.
    3.  **Recovery Mechanisms**: Automatic recovery from corruption or crashes.
    ```python
    class PersistenceManager:
        def save_state(self, state: QCState) -> None
        def load_state(self, state_id: UUID) -> QCState
        def create_snapshot(self, state: QCState) -> SnapshotId
        def restore_from_snapshot(self, snapshot_id: SnapshotId) -> QCState
    ```

---

### **File: `core/config_loader.py`**
*   **Purpose**: Loads and validates the main quantacirc.yml configuration with schema validation, environment variable substitution, and hierarchical configuration merging.
*   **Est. LOC**: 90
*   **Dependencies**: `yaml`, `pydantic`, `os`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Uses configuration data structures.
    *   `core/validators.py`: For configuration validation.
*   **Implementation Details**:
    1.  **Schema Validation**: JSON Schema validation for configuration files.
    2.  **Environment Substitution**: ${VAR} substitution in configuration values.
    3.  **Configuration Merging**: Hierarchical merging of multiple configuration sources.
    ```python
    class ConfigLoader:
        def load_config(self, config_path: Path) -> QuantaCircConfig
        def validate_config(self, config: Dict[str, Any]) -> ValidationResult
        def merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]
        def substitute_environment(self, config: Dict[str, Any]) -> Dict[str, Any]
    ```

---

### **File: `core/plugin_registry.py`**
*   **Purpose**: Simple plugin system for extending core functionality with custom energy functions, validators, and transformations while maintaining system integrity.
*   **Est. LOC**: 80
*   **Dependencies**: `importlib`, `typing`, `abc`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Uses plugin interface definitions.
*   **Implementation Details**:
    1.  **Plugin Discovery**: Automatic discovery of plugins in specified directories.
    2.  **Interface Enforcement**: Ensures plugins implement required interfaces.
    3.  **Safe Loading**: Sandboxed plugin loading with error isolation.
    ```python
    class PluginRegistry:
        def register_plugin(self, plugin: Plugin) -> None
        def discover_plugins(self, plugin_dir: Path) -> List[Plugin]
        def load_plugin(self, plugin_name: str) -> Plugin
        def validate_plugin(self, plugin: Plugin) -> ValidationResult
    ```

---

### **File: `core/utils.py`**
*   **Purpose**: Shared utility functions for the core package including mathematical helpers, data structure utilities, and common algorithms.
*   **Est. LOC**: 100
*   **Dependencies**: `typing`, `functools`, `itertools`.
*   **Internal Imports/Relationships**:
    *   `core/types.py`: Works with core data structures.
*   **Implementation Details**:
    1.  **Mathematical Utilities**: Common mathematical operations and transformations.
    2.  **Data Structure Helpers**: Utilities for working with complex data structures.
    3.  **Performance Utilities**: Caching, memoization, and optimization helpers.
    ```python
    def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]
    def normalize_vector(vector: np.ndarray) -> np.ndarray
    def cached_property(func): # Decorator for expensive property calculations
    def retry_with_backoff(max_retries: int, backoff_factor: float): # Decorator
    ```

---

## 3. Integration Architecture & Data Flow

### Mathematical Foundation Integration
The core package implements the complete mathematical framework described in the README:

1. **Energy Function (E_approx)**: Implemented across `energy_calculator.py`, `state_space.py`, and `metrics.py`
2. **Lyapunov Potential (Φ)**: Centralized in `lyapunov_monitor.py` with integration throughout the system
3. **Two-Phase Annealing**: Complete implementation in `two_phase_annealer.py` with convergence detection
4. **Functor Theory**: Bridge between software and quantum domains in `functor.py`
5. **Closure Rules (Δ)**: Formal constraint system in `closure_rules.py` and `constraint_solver.py`

### Data Flow Architecture
```
Configuration -> ConfigLoader -> QuantaCircConfig
    |
    v
Orchestrator -> EnergyCalculator -> QCState
    |              |
    v              v
AgentTasks -> RunLedger -> Persistence
    |
    v
TwoPhaseAnnealer -> ConvergenceEngine -> LyapunovMonitor
    |                      |
    v                      v
StateTransitions -> ClosureRules -> ConstraintSolver
```

### Error Handling Strategy
- **Structured Exceptions**: All errors are instances of `QuantaCircError` with context
- **Error Budgets**: Economic model of error tolerance via `ErrorBudgetManager`
- **Validation Layers**: Multiple validation points ensure data integrity
- **Recovery Mechanisms**: Automatic recovery and rollback capabilities

### Performance Considerations
- **Incremental Computation**: Energy and Lyapunov calculations are incremental
- **Caching Strategy**: Multi-level caching for expensive computations
- **Asynchronous Operations**: Non-blocking orchestration with async/await
- **Memory Management**: Efficient state representation and garbage collection

This comprehensive plan ensures that the core package provides a solid mathematical and architectural foundation for the entire QuantaCirc system while maintaining performance, reliability, and extensibility.
