# Plan for the `agents` Directory - Complete Implementation Guide

## 1. Guiding Philosophy & Core Principles

The `agents` directory embodies the agentic architecture at the heart of QuantaCirc. Ten specialized, autonomous agents collaborate to transform software systems according to quantum-mechanical principles, each targeting specific aspects of the energy function `E_approx`.

### Core Design Principles

1. **Single Responsibility & Specialization**: Each agent targets one specific component of software quality
2. **Contract-Based Operation**: Strict `Precondition → Propose → Verify → Execute` cycle
3. **Rigor Classification**: Operations classified as Functor-Verified, Empirically-Validated, or Heuristic-Inspired
4. **Quantum State Awareness**: All agents operate within quantum state representation `ρ`
5. **Stateless Workers**: Pure functions `S_t → S_{t+1}` with no internal state

---

## 2. Base Infrastructure (10 Files)

### `agents/__init__.py` (5 LOC)
Package initializer exposing QuantumAgent and AgentRouter classes.

### `agents/base/__init__.py` (5 LOC) 
Base framework initializer for agent infrastructure.

### `agents/base/agent.py` (150 LOC)
**Purpose**: Abstract base class defining agent contract and common functionality.
**Key Features**: Abstract methods for analyze_state(), validate_proposal(), execution lifecycle management, metrics integration, contract enforcement.

### `agents/base/prompts.py` (50 LOC)
**Purpose**: Prompt management with versioning and integrity checking.
**Key Features**: PromptSpec dataclass with checksums, PromptRegistry for version control, YAML loading capabilities.

### `agents/base/ops.py` (80 LOC)
**Purpose**: Shared operations library for code analysis.
**Key Features**: AST parsing, function/class extraction, complexity metrics, duplicate detection, dependency analysis.

### `agents/base/memory.py` (100 LOC)
**Purpose**: Interface to Constellation memory system for agent learning.
**Key Features**: AgentMemory abstract interface, decision storage, similarity search, pattern learning, feedback integration.

### `agents/base/metrics.py` (60 LOC)
**Purpose**: Prometheus metrics collection for agent performance.
**Key Features**: Execution counters, duration histograms, energy impact tracking, success rates, error counting.

### `agents/base/policies.py` (70 LOC)
**Purpose**: Policy framework for agent action validation.
**Key Features**: RigorPolicy, EnergyBudgetPolicy, PolicyEngine with aggregation logic.

### `agents/base/contracts.py` (90 LOC)
**Purpose**: Pre/postcondition contract enforcement.
**Key Features**: Condition abstract class, EnergyCondition, LyapunovCondition, ClosureRuleCondition, contract validation.

### `agents/base/router.py` (120 LOC)
**Purpose**: Task routing to appropriate agents based on capabilities.
**Key Features**: Capability matching, performance scoring, priority queuing, routing decisions with confidence scores.

---

## 3. Specialized Agents (30 Files - 10 Agents × 3 Files Each)

### PlanckForge Agent (Requirements Quantizer)
**Files**: `agents/planck_forge/agent.py` (250 LOC), `prompts.py` (100 LOC), `ops.py` (150 LOC)
**Purpose**: Translates natural language requirements into formal, verifiable task sets.
**Rigor**: Functor-Verified
**Energy Target**: E_static (requirement complexity)
**Key Features**: LLM-based requirement decomposition, closure rule application, task DAG generation, dependency analysis.

### SchrodingerDev Agent (Code & Proof Generator)
**Files**: `agents/schrodinger_dev/agent.py` (300 LOC), `prompts.py` (150 LOC), `ops.py` (200 LOC)
**Purpose**: Generates code and proof skeletons from formal task specifications.
**Rigor**: Empirically-Validated  
**Energy Target**: E_static + E_dynamic (code generation quality)
**Key Features**: Template-driven code generation, proof skeleton creation, type-safe code synthesis, verification integration.

### PauliGuard Agent (Orthogonality Enforcer)
**Files**: `agents/pauli_guard/agent.py` (280 LOC), `prompts.py` (100 LOC), `ops.py` (180 LOC)
**Purpose**: Detects and eliminates code duplication to maintain orthogonality.
**Rigor**: Functor-Verified
**Energy Target**: E_interaction (coupling reduction)
**Key Features**: Duplicate detection algorithms, refactoring plan generation, similarity analysis, automated deduplication.

### UncertainAI Agent (Risk Manager)
**Files**: `agents/uncertain_ai/agent.py` (260 LOC), `prompts.py` (120 LOC), `ops.py` (160 LOC)
**Purpose**: Manages uncertainty and generates tests to reduce system risk.
**Rigor**: Empirically-Validated
**Energy Target**: E_dynamic (uncertainty reduction)
**Key Features**: Risk assessment, test case generation, uncertainty quantification, coverage analysis.

### TunnelFix Agent (Performance Optimizer)
**Files**: `agents/tunnel_fix/agent.py` (220 LOC), `prompts.py` (80 LOC), `ops.py` (140 LOC)
**Purpose**: Identifies and optimizes performance bottlenecks.
**Rigor**: Empirically-Validated
**Energy Target**: E_dynamic (runtime performance)
**Key Features**: Performance profiling, bottleneck detection, optimization suggestions, benchmarking integration.

### BoseBoost Agent (Scaling Coordinator)
**Files**: `agents/bose_boost/agent.py` (200 LOC), `prompts.py` (70 LOC), `ops.py` (130 LOC)
**Purpose**: Manages collective scaling and deployment configurations.
**Rigor**: Heuristic-Inspired
**Energy Target**: E_interaction (system scaling)
**Key Features**: Kubernetes manifest generation, HPA configuration, resource optimization, capacity planning.

### PhononFlow Agent (Data Flow Optimizer)
**Files**: `agents/phonon_flow/agent.py` (210 LOC), `prompts.py` (70 LOC), `ops.py` (130 LOC)
**Purpose**: Optimizes data flow and communication patterns.
**Rigor**: Empirically-Validated
**Energy Target**: E_interaction (data flow efficiency)
**Key Features**: Data flow analysis, communication optimization, pipeline design, streaming optimization.

### FluctuaTest Agent (Chaos Engineer)
**Files**: `agents/fluctua_test/agent.py` (240 LOC), `prompts.py` (90 LOC), `ops.py` (150 LOC)
**Purpose**: Runs chaos tests to ensure system stability under stress.
**Rigor**: Empirically-Validated
**Energy Target**: E_dynamic (system resilience)
**Key Features**: Chaos test generation, fault injection, stability analysis, resilience measurement.

### HydroSpread Agent (Growth Modeler)
**Files**: `agents/hydro_spread/agent.py` (180 LOC), `prompts.py` (60 LOC), `ops.py` (110 LOC)
**Purpose**: Models and forecasts system growth and complexity evolution.
**Rigor**: Heuristic-Inspired
**Energy Target**: E_static (complexity forecasting)
**Key Features**: Growth pattern analysis, complexity prediction, scaling law modeling, trend analysis.

### LondonLink Agent (Dependency Manager)
**Files**: `agents/london_link/agent.py` (230 LOC), `prompts.py` (80 LOC), `ops.py` (140 LOC)
**Purpose**: Manages and optimizes external dependencies.
**Rigor**: Empirically-Validated
**Energy Target**: E_interaction (dependency optimization)
**Key Features**: Dependency analysis, vulnerability scanning, SBOM generation, version optimization.

---

## 4. Implementation Strategy

### Agent Lifecycle
1. **Registration**: Agents register with orchestrator and router
2. **Activation**: Triggered by state conditions and task availability  
3. **Analysis**: Examine current state for optimization opportunities
4. **Proposal**: Generate formal proposals with energy predictions
5. **Validation**: Contract and policy checking before execution
6. **Execution**: Coordinate with orchestrator for state transitions
7. **Feedback**: Collect metrics and update performance history

### Inter-Agent Coordination
- **Message Bus**: Asynchronous communication via NATS
- **State Synchronization**: Shared quantum state representation
- **Conflict Resolution**: Priority-based task scheduling
- **Collaborative Filtering**: Agents can veto problematic proposals

### Quality Assurance
- **Contract Enforcement**: Mathematical pre/postconditions
- **Rigor Classification**: Runtime rigor level enforcement
- **Energy Budgets**: Prevent energy increases beyond thresholds
- **Lyapunov Monitoring**: Ensure convergence properties maintained

### Performance Optimization
- **Lazy Loading**: Agents loaded on-demand
- **Caching**: Expensive analysis results cached
- **Parallel Execution**: Non-conflicting agents run in parallel
- **Performance Tracking**: Continuous performance monitoring

This comprehensive agent ecosystem ensures quantum-mechanical software engineering principles are applied systematically and measurably across all aspects of system evolution.
