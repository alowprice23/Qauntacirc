# QuantaCirc Implementation Prompts - Complete System Design

## Master Implementation Guide for Agentic Software Engineer

This document provides the definitive sequence of prompts for implementing the complete QuantaCirc system - a quantum-mechanical software engineering platform. Each prompt builds upon previous implementations, creating a domino effect that ensures no component is overlooked and the system maintains mathematical consistency throughout.

**Total System Scope**: ~200+ files across 15+ directories with rigorous mathematical foundations.

---

## PHASE 1: MATHEMATICAL FOUNDATION & CORE INFRASTRUCTURE

### Prompt 1: Core Mathematical Framework (`/math` - 25 files)

**CRITICAL FIRST STEP**: Implement the complete mathematical foundation that underpins all QuantaCirc operations.

```
Create the mathematical foundation for QuantaCirc in the `/math` directory. This is the FIRST and MOST CRITICAL implementation as all other systems depend on these mathematical primitives.

REQUIRED FILES (implement ALL 25 files):

1. `/math/__init__.py` (5 LOC)
   - Export LyapunovFunction, StabilityAnalyzer, TwoPhaseAnnealer, TemperatureSchedule
   - Export UncertaintyQuantifier, ConfidenceBounds

2. `/math/annealing.py` (150 LOC)
   - TwoPhaseAnnealer class with quantum-mechanical temperature schedules
   - Adaptive temperature scheduling for exploration/exploitation phases
   - Metropolis acceptance with quantum tunneling corrections
   - Phase transition detection based on energy variance
   - Mathematical convergence guarantees through Markov chain theory

3. `/math/lyapunov.py` (130 LOC)
   - LyapunovFunction class for stability analysis
   - Quadratic and general Lyapunov function implementations
   - Stability analysis using Lyapunov's direct method
   - Exponential stability rate estimation
   - Convergence trajectory validation

4. `/math/contractive_maps.py` (100 LOC)
   - Contraction mapping theory for fixed-point convergence
   - Banach fixed-point theorem implementation
   - Contraction factor computation and verification
   - Convergence rate analysis for iterative methods

5. `/math/pl_inequality.py` (80 LOC)
   - Polyak-Łojasiewicz inequality for optimization convergence rates
   - PL inequality verification for energy functions
   - Global optimization convergence rate bounds
   - Non-convex optimization guarantees

6. `/math/martingales.py` (80 LOC)
   - Martingale theory for stochastic convergence analysis
   - Doob's martingale convergence theorem applications
   - Azuma-Hoeffding concentration inequalities
   - Optional stopping theorem for optimization bounds

7. `/math/hessian_free.py` (110 LOC)
   - Hessian-free optimization methods for large-scale systems
   - Conjugate gradient methods avoiding explicit Hessian computation
   - Pearlmutter algorithm for efficient Hessian-vector products

8. `/math/line_search.py` (70 LOC)
   - Line search algorithms ensuring sufficient decrease
   - Armijo backtracking with polynomial interpolation
   - Wolfe conditions for curvature requirements

9. `/math/stopping_rules.py` (90 LOC)
   - Stopping criteria for optimization algorithms
   - Gradient norm-based stopping with adaptive thresholds
   - Energy stabilization detection with confidence intervals

10. `/math/verification_utils.py` (100 LOC)
    - Mathematical verification utilities for optimization convergence proofs
    - Convergence certificate generation with mathematical proofs
    - Lipschitz constant verification for optimization theory

[Continue with remaining 15 mathematical files: graph_spectra.py, laplacian.py, info_entropy.py, kolmogorov_bounds.py, distance_metrics.py, lipschitz.py, uncertainty_bounds.py, statistics.py, distributions.py, estimation.py, samplers.py, markov_chains.py, random_processes.py, dim_analysis.py, units.py, green_kubo.py]

IMPLEMENTATION REQUIREMENTS:
- All functions must be mathematically rigorous with numerical stability
- Include comprehensive docstrings with mathematical formulations
- Implement property-based tests for all mathematical functions
- Use numpy/scipy for vectorized operations
- Each file must export clear public APIs
- Mathematical properties must be verifiable through formal proofs

DEPENDENCIES: None (this is the foundation)
BLOCKS: All other system components depend on this mathematical foundation
```

### Prompt 2: Core System Types & Data Architecture (`/core/types.py`)

**SECOND CRITICAL STEP**: Define the complete data architecture that all components will use.

```
Implement the complete type system for QuantaCirc in `/core/types.py`. This defines the data architecture backbone used throughout the entire system.

REQUIRED IMPLEMENTATION (180 LOC):

Create comprehensive Pydantic models:

1. **QCState** - Core software system state representation
   - id: UUID
   - timestamp: datetime  
   - software_state: SoftwareState
   - quantum_state: Optional[QuantumState]
   - energy: float
   - energy_components: EnergyComponents
   - lyapunov_potential: float
   - contraction_factor: float
   - optimization_phase: str
   - metadata: Dict[str, Any]

2. **EnergyComponents** - Energy function decomposition
   - static: float
   - dynamic: float
   - interaction: float
   - total: float (computed property)

3. **AgentTask** - Communication protocol for agent requests
   - id: UUID
   - agent_name: str
   - task_type: str
   - payload: Dict[str, Any]
   - priority: int
   - quantum_context: Optional[QCState]
   - created_at: datetime

4. **AgentResult** - Communication protocol for agent responses
   - task_id: UUID
   - agent_name: str
   - action_taken: bool
   - energy_delta: Optional[Dict[str, float]]
   - error: Optional[str]
   - artifacts: List[str]
   - verification_required: bool

[Continue defining ALL core types: LyapunovResult, StateTransformation, ConstraintViolation, SMTResult, ProofCertificate, RunRecord, VerificationReport, etc.]

VALIDATION REQUIREMENTS:
- All fields must have proper type annotations
- Include comprehensive validation rules
- Implement serialization/deserialization methods
- Add mathematical constraint validators
- Include JSON schema generation

DEPENDENCIES: math/ (for mathematical types)
BLOCKS: All other system components require these types
```

### Prompt 3: Core Infrastructure Implementation (`/core` - 18 remaining files)

**THIRD STEP**: Implement the core computational engine using the mathematical foundation and types.

```
Implement the complete core infrastructure for QuantaCirc in the `/core` directory. This creates the computational heart of the quantum-mechanical system.

REQUIRED FILES (implement ALL 18 files in sequence):

1. `/core/__init__.py` (25 LOC)
   - Export Orchestrator, EnergyCalculator, Functor, RunLedger
   - Export QCState, QCEnergy from types
   - Export ConstraintSolver, LyapunovMonitor
   - Establish clean public API with __all__ list

2. `/core/energy_calculator.py` (350 LOC) - CRITICAL DEPENDENCY
   - EnergyCalculator class implementing E_approx = E_static + E_dynamic + E_interaction
   - compute_static_energy(): Code complexity, coupling, cohesion metrics
   - compute_dynamic_energy(): Runtime performance, memory usage patterns
   - compute_interaction_energy(): Inter-module dependencies, API surface areas
   - energy_gradient() and energy_hessian() for optimization
   - Incremental computation with caching strategy
   - Integration with math/annealing.py and math/lyapunov.py

3. `/core/lyapunov_monitor.py` (220 LOC) - CRITICAL DEPENDENCY
   - LyapunovMonitor class for Φ(S_t) computation
   - track_excursion(): Bounded excursion monitoring
   - verify_stability(): Stability analysis using math/lyapunov.py
   - predict_convergence(): Convergence time estimation
   - Martingale property verification using math/martingales.py

4. `/core/two_phase_annealer.py` (300 LOC) - CRITICAL DEPENDENCY
   - TwoPhaseAnnealer implementation using math/annealing.py
   - phase_a_step(): High temperature exploration
   - phase_b_step(): Low temperature exploitation  
   - Temperature schedule using math/annealing.TemperatureSchedule
   - Convergence detection using math/contractive_maps.py

5. `/core/functor.py` (300 LOC)
   - SoftSys -> QuantSys functor implementation
   - map_software_to_quantum(): Convert software artifacts to quantum states
   - compute_density_matrix(): Quantum state representation
   - evolve_quantum_state(): Unitary evolution operations
   - measure_observable(): Extract measurements from quantum states

6. `/core/constraint_solver.py` (180 LOC)
   - ConstraintSolver class with Z3 integration
   - add_constraint(), check_satisfiability(), get_model()
   - generate_proof_certificate(): Formal proof generation
   - Integration with closure_rules.py for constraint checking

7. `/core/closure_rules.py` (150 LOC)
   - ClosureRuleSet for Δ consistency rule management
   - validate_transition(): State transition validation
   - suggest_fixes(): Automated fix suggestions for violations
   - Integration with constraint_solver.py

[Continue with remaining 11 core files: orchestrator.py, convergence_engine.py, run_ledger.py, error_budget.py, state_space.py, edit_distance.py, metrics.py, validators.py, exceptions.py, serialization.py, persistence.py, config_loader.py, plugin_registry.py, utils.py]

SEQUENCING REQUIREMENTS:
1. Implement energy_calculator.py FIRST (everything depends on energy computation)
2. Implement lyapunov_monitor.py SECOND (stability monitoring required)
3. Implement two_phase_annealer.py THIRD (optimization engine)
4. Implement remaining files in dependency order

DEPENDENCIES: math/, core/types.py
BLOCKS: agents/, messaging/, monitoring/, cli/
```

---

## PHASE 2: MESSAGING & COMMUNICATION INFRASTRUCTURE

### Prompt 4: Messaging Infrastructure (`/messaging` - 10 files)

**FOURTH STEP**: Implement the complete messaging system for agent communication.

```
Implement the complete NATS-based messaging infrastructure in `/messaging`. This enables asynchronous communication between all QuantaCirc components while maintaining quantum state consistency.

REQUIRED FILES (implement ALL 10 files):

1. `/messaging/__init__.py` (5 LOC)
   - Export NATSClient, MessagePublisher, MessageSubscriber, StreamManager

2. `/messaging/nats_client.py` (180 LOC) - CORE DEPENDENCY
   - NATSClient class with quantum state context propagation
   - Connection management with automatic failover
   - JetStream context management for persistent messaging
   - publish_quantum_message(): Message publishing with quantum context
   - subscribe_quantum_aware(): Context-aware subscriptions
   - Quantum state encoding/decoding in message headers

3. `/messaging/publisher.py` (80 LOC)
   - MessagePublisher with batching and compression
   - Quantum state validation before publishing
   - Retry logic with exponential backoff
   - Message deduplication and idempotency

4. `/messaging/subscriber.py` (80 LOC)
   - MessageSubscriber with automatic processing
   - Dead letter queue integration
   - Quantum state validation on received messages
   - Circuit breaker pattern for failing consumers

5. `/messaging/stream_manager.py` (100 LOC)
   - StreamManager for NATS stream lifecycle
   - Stream creation and configuration
   - Consumer group management
   - Performance monitoring and optimization

6. `/messaging/topic_manager.py` (70 LOC)
   - Topic schema management and routing
   - Schema registry integration
   - Topic lifecycle management
   - Access control integration

7. `/messaging/serialization.py` (90 LOC)
   - MessageSerializer with multiple formats (JSON, MessagePack, Protobuf)
   - Automatic compression for large messages
   - Schema versioning support
   - Type-safe serialization with validation

8. `/messaging/middleware/__init__.py` (5 LOC)
   - Export all middleware components

9. `/messaging/middleware/logging.py` (60 LOC)
   - LoggingMiddleware for structured message logging
   - Audit trail generation
   - Performance metrics logging
   - Error event correlation

10. `/messaging/middleware/validation.py` (60 LOC)
    - ValidationMiddleware for message integrity
    - Schema validation for payloads
    - Quantum state consistency checking
    - Security checks and sanitization

IMPLEMENTATION REQUIREMENTS:
- All messaging must preserve quantum state context
- Implement comprehensive error handling and retry logic
- Ensure message ordering preserves causality
- Include performance optimization (batching, compression)
- Integrate with monitoring for observability

DEPENDENCIES: core/ (types, quantum state management)
BLOCKS: agents/ (agent communication requires messaging)
```

---

## PHASE 3: MONITORING & OBSERVABILITY SYSTEM

### Prompt 5: Monitoring Infrastructure (`/monitoring` - 15 files)

**FIFTH STEP**: Implement comprehensive observability for quantum system monitoring.

```
Implement the complete monitoring infrastructure in `/monitoring`. This provides observability into quantum state evolution, agent behavior, and system performance.

REQUIRED FILES (implement ALL 15 files):

1. `/monitoring/__init__.py` (5 LOC)
   - Export QuantumMetrics, QuantumTracer, StructuredLogger, AnomalyDetector

2. `/monitoring/metrics.py` (150 LOC) - CORE METRICS ENGINE
   - QuantumMetrics class with Prometheus integration
   - Quantum state metrics (energy, Lyapunov, phase tracking)
   - Agent performance metrics (execution time, success rates)
   - System resource metrics (CPU, memory, connections)
   - Mathematical convergence metrics
   - record_quantum_state(), record_agent_execution(), record_llm_usage()

3. `/monitoring/tracing.py` (120 LOC)
   - QuantumTracer with OpenTelemetry integration
   - Distributed trace collection across agent boundaries
   - Quantum state context propagation in traces
   - Custom span attributes for quantum measurements
   - Performance bottleneck identification

4. `/monitoring/logging.py` (100 LOC)
   - StructuredLogger with quantum context integration
   - JSON structured logging with quantum state context
   - Centralized log aggregation
   - Correlation ID tracking for distributed operations
   - Performance-optimized async logging

5. `/monitoring/anomaly_detector.py` (150 LOC)
   - QuantumAnomalyDetector using machine learning
   - Quantum state anomaly detection using statistical methods
   - Agent behavior pattern analysis
   - Performance regression detection
   - Automated alert generation for anomalies

6. `/monitoring/exporters/__init__.py` (5 LOC)
   - Export PrometheusExporter, JaegerExporter, ElasticsearchExporter

7. `/monitoring/exporters/prometheus.py` (80 LOC)
   - PrometheusExporter with custom collectors
   - Quantum-specific metrics formatting
   - High-cardinality metrics optimization
   - Push gateway integration

8. `/monitoring/exporters/jaeger.py` (80 LOC)
   - JaegerExporter with quantum context preservation
   - OpenTelemetry to Jaeger export
   - Trace sampling optimization
   - Custom trace processors for quantum measurements

9. `/monitoring/exporters/elasticsearch.py` (80 LOC)
   - ElasticsearchExporter for log aggregation
   - Structured log export to Elasticsearch
   - Index template management
   - Search-optimized field mapping

10. `/monitoring/dashboards/grafana.json` (500 LOC)
    - Complete Grafana dashboard configuration
    - Quantum state evolution visualization
    - Agent performance dashboards
    - Mathematical convergence tracking
    - Real-time alerting integration

[Continue with remaining 5 files: health/readiness.py, health/liveness.py, health/dependency.py, dashboards/prometheus.yml, dashboards/jaeger.yml]

IMPLEMENTATION REQUIREMENTS:
- All monitoring must be quantum-aware (track energy, Lyapunov, phase)
- Low-overhead monitoring that doesn't impact performance
- Real-time alerting for critical quantum state changes
- Integration with standard observability tools (Prometheus, Grafana, Jaeger)

DEPENDENCIES: core/ (quantum state access), messaging/ (message monitoring)
BLOCKS: agents/ (agents need monitoring integration)
```

---

## PHASE 4: AGENT ECOSYSTEM IMPLEMENTATION

### Prompt 6: Agent Base Infrastructure (`/agents/base` - 10 files)

**SIXTH STEP**: Implement the agent framework before individual agents.

```
Implement the complete agent base infrastructure in `/agents/base`. This provides the foundation that all specialized agents will inherit from.

REQUIRED FILES (implement ALL 10 files in sequence):

1. `/agents/__init__.py` (5 LOC)
   - Export QuantumAgent, AgentRouter from base framework

2. `/agents/base/__init__.py` (5 LOC)
   - Export agent base classes and utilities

3. `/agents/base/agent.py` (150 LOC) - CRITICAL FOUNDATION
   - QuantumAgent abstract base class
   - Abstract methods: analyze_state(), validate_proposal(), execute()
   - Contract enforcement with preconditions/postconditions
   - Metrics integration with monitoring/metrics.py
   - Quantum state awareness and energy impact tracking
   - Lifecycle management (initialize, activate, deactivate)

4. `/agents/base/contracts.py` (90 LOC)
   - Contract enforcement framework
   - EnergyCondition, LyapunovCondition, ClosureRuleCondition
   - Contract validation before/after agent execution
   - Integration with core/constraint_solver.py

5. `/agents/base/policies.py` (70 LOC)
   - Policy framework for agent action validation
   - RigorPolicy, EnergyBudgetPolicy classes
   - PolicyEngine with aggregation logic
   - Integration with core/error_budget.py

6. `/agents/base/memory.py` (100 LOC)
   - AgentMemory interface to Constellation memory system
   - Decision storage and retrieval
   - Pattern learning and similarity search
   - Integration with memory/constellation.py

7. `/agents/base/metrics.py` (60 LOC)
   - Agent-specific metrics collection
   - Execution counters, duration histograms
   - Energy impact tracking, success rates
   - Integration with monitoring/metrics.py

8. `/agents/base/ops.py` (80 LOC)
   - Shared operations library for code analysis
   - AST parsing, function/class extraction
   - Complexity metrics, duplicate detection
   - Common utilities used by all agents

9. `/agents/base/prompts.py` (50 LOC)
   - Prompt management with versioning
   - PromptSpec dataclass with checksums
   - PromptRegistry for version control
   - YAML loading capabilities

10. `/agents/base/router.py` (120 LOC)
    - AgentRouter for task routing
    - Capability matching and performance scoring
    - Priority queuing and routing decisions
    - Load balancing across agent instances

IMPLEMENTATION REQUIREMENTS:
- All agents must inherit from QuantumAgent base class
- Comprehensive contract enforcement for mathematical guarantees
- Integration with quantum state management
- Metrics collection for all agent operations

DEPENDENCIES: core/, messaging/, monitoring/
BLOCKS: Individual agent implementations depend on this base
```

### Prompt 7: Specialized Agents Implementation (`/agents` - 30 agent files)

**SEVENTH STEP**: Implement all 10 specialized agents with their support files.

```
Implement ALL 10 specialized agents in `/agents`. Each agent has 3 files (agent.py, prompts.py, ops.py) for a total of 30 files. Implement in the specified order to maintain dependencies.

AGENT IMPLEMENTATION ORDER (implement in this exact sequence):

1. **PlanckForge Agent** (Requirement Quantizer) - IMPLEMENT FIRST
   Files: `/agents/planck_forge/agent.py` (250 LOC), `prompts.py` (100 LOC), `ops.py` (150 LOC)
   Purpose: Translates natural language requirements into formal task sets
   Rigor: Functor-Verified
   Energy Target: E_static (requirement complexity)
   Key Features: LLM-based requirement decomposition, closure rule application, task DAG generation
   Dependencies: agents/base/, core/, llm/, messaging/

2. **SchrodingerDev Agent** (Code & Proof Generator) - IMPLEMENT SECOND
   Files: `/agents/schrodinger_dev/agent.py` (300 LOC), `prompts.py` (150 LOC), `ops.py` (200 LOC)
   Purpose: Generates code and proof skeletons from formal task specifications
   Rigor: Empirically-Validated
   Energy Target: E_static + E_dynamic (code generation quality)
   Key Features: Template-driven code generation, proof skeleton creation, type-safe synthesis
   Dependencies: PlanckForge results, agents/base/, templates/

3. **PauliGuard Agent** (Orthogonality Enforcer) - IMPLEMENT THIRD
   Files: `/agents/pauli_guard/agent.py` (280 LOC), `prompts.py` (100 LOC), `ops.py` (180 LOC)
   Purpose: Detects and eliminates code duplication to maintain orthogonality
   Rigor: Functor-Verified
   Energy Target: E_interaction (coupling reduction)
   Key Features: Duplicate detection algorithms, refactoring plan generation, similarity analysis
   Dependencies: SchrodingerDev outputs, agents/base/

4. **UncertainAI Agent** (Risk Manager) - IMPLEMENT FOURTH
   Files: `/agents/uncertain_ai/agent.py` (260 LOC), `prompts.py` (120 LOC), `ops.py` (160 LOC)
   Purpose: Manages uncertainty and generates tests to reduce system risk
   Rigor: Empirically-Validated
   Energy Target: E_dynamic (uncertainty reduction)
   Key Features: Risk assessment, test case generation, uncertainty quantification
   Dependencies: PauliGuard analysis, agents/base/, math/uncertainty_bounds.py

[Continue with remaining 6 agents in dependency order: TunnelFix, BoseBoost, PhononFlow, FluctuaTest, HydroSpread, LondonLink]

FOR EACH AGENT, IMPLEMENT:

**agent.py Structure:**
- Class inheriting from agents.base.agent.QuantumAgent  
- analyze_state() method for state analysis
- generate_proposals() method for action proposals
- validate_proposal() method for proposal validation
- execute() method for action execution
- Integration with messaging/ for communication
- Energy impact calculation and reporting
- Contract enforcement with preconditions/postconditions

**prompts.py Structure:**
- LLM prompt templates specific to agent function
- Prompt versioning and integrity checking
- Parameter substitution and validation
- Response parsing and quality assessment

**ops.py Structure:**
- Agent-specific operations and utilities
- Code analysis functions specific to agent domain
- Integration with shared agents/base/ops.py utilities
- Domain-specific algorithms and computations

IMPLEMENTATION REQUIREMENTS:
- Implement agents in the specified dependency order
- Each agent must maintain mathematical rigor classification
- All agents must integrate with quantum state management
- Energy impact must be computed and reported for all actions
- Comprehensive error handling and recovery

DEPENDENCIES: agents/base/, core/, messaging/, monitoring/, llm/
BLOCKS: CLI generate command requires all agents operational
```

---

## PHASE 5: LLM INTEGRATION SYSTEM

### Prompt 8: LLM Integration Infrastructure (`/llm` - 8 files)

**EIGHTH STEP**: Implement the complete LLM integration system for agent natural language processing.

```
Implement the complete LLM integration system in `/llm`. This enables agents to leverage multiple LLM providers while maintaining quantum state awareness and cost optimization.

REQUIRED FILES (implement ALL 8 files):

1. `/llm/__init__.py` (5 LOC)
   - Export LLMClient, OpenAIClient, AnthropicClient, GroqClient, GeminiClient

2. `/llm/client.py` (150 LOC) - ABSTRACT BASE CLASS
   - LLMClient abstract base class
   - Abstract methods: generate(), chat(), embed()
   - Quantum context integration
   - Cost tracking and budget management
   - Rate limiting and retry logic
   - Response validation and safety filtering

3. `/llm/openai_client.py` (120 LOC)
   - OpenAIClient implementation
   - GPT-4, GPT-3.5 model support
   - Function calling integration
   - Token usage tracking and cost calculation
   - Rate limiting compliance

4. `/llm/anthropic_client.py` (120 LOC)
   - AnthropicClient for Claude integration
   - Constitutional AI compliance
   - Safety filtering integration
   - Message formatting and parsing
   - Token optimization

5. `/llm/groq_client.py` (100 LOC)
   - GroqClient for high-speed inference
   - LPU integration and optimization
   - Performance benchmarking
   - Latency measurement and reporting

6. `/llm/gemini_client.py` (100 LOC)
   - GeminiClient for multimodal capabilities
   - Code understanding optimization
   - Safety integration
   - Multimodal input handling

7. `/llm/rate_limiter.py` (80 LOC)
   - RateLimiter with quantum-aware throttling
   - Token bucket algorithms
   - Cost tracking and budget enforcement
   - Adaptive limiting based on quantum state

8. `/llm/validators.py` (60 LOC)
   - Response validation framework
   - Quantum constraint checking
   - Safety filtering and content analysis
   - Quality assessment and scoring

IMPLEMENTATION REQUIREMENTS:
- All LLM clients must implement the abstract LLMClient interface
- Quantum context must be preserved across LLM interactions
- Comprehensive cost tracking and budget management
- Rate limiting to prevent API quota exhaustion
- Safety filtering for all LLM responses

DEPENDENCIES: core/ (quantum state integration)
BLOCKS: agents/ require LLM integration for natural language processing
```

---

## PHASE 6: COMMAND LINE INTERFACE

### Prompt 9: CLI Implementation (`/cli` - 14 files)

**NINTH STEP**: Implement the complete command-line interface that orchestrates the entire system.

```
Implement the complete CLI system in `/cli`. This provides the primary human interface to the QuantaCirc system with quantum-aware commands and rich output formatting.

REQUIRED FILES (implement ALL 14 files in sequence):

1. `/cli/__init__.py` (5 LOC)
   - Export cli_app and version information

2. `/cli/main.py` (150 LOC) - PRIMARY ENTRY POINT
   - Main Typer application with quantum theming
   - Global configuration and context management
   - Version callback with rich formatting
   - Quantum state verification on startup
   - Comprehensive error handling
   - Integration with all command modules

3. `/cli/commands/__init__.py` (5 LOC)
   - Export all command modules

4. `/cli/commands/init.py` (80 LOC)
   - `qc init` command implementation
   - Project scaffolding with quantum state initialization
   - Template-based project generation
   - Energy function calibration
   - Configuration file creation

5. `/cli/commands/generate.py` (120 LOC) - CORE COMMAND
   - `qc generate` command for agentic code generation
   - Natural language requirement processing
   - Agent pipeline orchestration
   - Real-time quantum state monitoring
   - Verification gate enforcement
   - Interactive and non-interactive modes

6. `/cli/commands/verify.py` (90 LOC)
   - `qc verify` command for formal verification
   - Coq/Agda proof validation
   - SMT constraint checking
   - Energy function validation
   - Comprehensive verification reporting

7. `/cli/commands/deploy.py` (100 LOC)
   - `qc deploy` command for deployment
   - Pre-deployment verification gates
   - Multi-environment deployment support
   - Quantum state preservation across deployments
   - Rollback capability with state restoration

8. `/cli/commands/demo.py` (70 LOC)
   - `qc demo` command for demonstrations
   - Pre-built demonstration scenarios
   - Interactive tutorial mode
   - Agent capability showcases

9. `/cli/commands/status.py` (60 LOC)
   - `qc status` command for system monitoring
   - Real-time quantum state display (E_approx, Φ, λ)
   - Agent pipeline status monitoring
   - System health indicators
   - Watch mode with continuous updates

10. `/cli/commands/memory.py` (80 LOC)
    - `qc memory` command for Constellation memory interaction
    - Memory query and search operations
    - Pattern analysis and insights
    - Memory cleanup and maintenance

11. `/cli/formatters/__init__.py` (5 LOC)
    - Export formatting utilities

12. `/cli/formatters/table.py` (100 LOC)
    - Rich table formatting with quantum theming
    - QuantumTable, StatusTable, MetricsTable classes
    - Energy component visualization
    - Mathematical formula rendering
    - Consistent color schemes

IMPLEMENTATION REQUIREMENTS:
- All commands must be quantum-aware and display quantum state
- Rich formatting with consistent quantum theming
- Comprehensive error handling with structured errors
- Integration with all system components
- Interactive and non-interactive modes support

DEPENDENCIES: ALL previous phases (core/, agents/, messaging/, monitoring/, llm/)
BLOCKS: This is the primary user interface - system unusable without CLI
```

---

## PHASE 7: TESTING INFRASTRUCTURE

### Prompt 10: Comprehensive Testing System (`/tests` - 100+ files)

**TENTH STEP**: Implement the complete testing infrastructure to ensure system correctness.

```
Implement the comprehensive testing system in `/tests`. This ensures mathematical correctness, system reliability, and agent coordination through extensive testing coverage.

REQUIRED TEST STRUCTURE (implement ALL test categories):

1. **Test Infrastructure** (2 files)
   - `/tests/__init__.py` (5 LOC): Package configuration
   - `/tests/conftest.py` (100 LOC): Pytest configuration with quantum-aware fixtures

2. **Unit Tests - Core System** (15 files, ~1500 LOC)
   - `/tests/unit/core/test_orchestrator.py`: Main orchestration engine testing
   - `/tests/unit/core/test_energy_calculator.py`: Energy function computation testing
   - `/tests/unit/core/test_lyapunov_monitor.py`: Lyapunov function and stability testing
   - `/tests/unit/core/test_two_phase_annealer.py`: Annealing algorithm testing
   - `/tests/unit/core/test_functor.py`: Category theory functor testing
   - `/tests/unit/core/test_constraint_solver.py`: SMT constraint solver testing
   - [Continue with remaining 9 core unit test files]

3. **Unit Tests - Agent System** (32 files, ~3200 LOC)
   - `/tests/unit/agents/test_base_agent.py`: Base agent abstract class testing
   - `/tests/unit/agents/test_planck_forge.py`: PlanckForge agent testing
   - `/tests/unit/agents/test_schrodinger_dev.py`: SchrodingerDev agent testing
   - [Continue with all 10 agents × 3 files each + base infrastructure]

4. **Unit Tests - Math System** (17 files, ~1700 LOC)
   - `/tests/unit/math/test_annealing.py`: Annealing algorithm testing
   - `/tests/unit/math/test_lyapunov.py`: Lyapunov function testing
   - [Continue with all 25 mathematical modules]

5. **Integration Tests** (25 files, ~2500 LOC)
   - `/tests/integration/test_agent_coordination.py`: Multi-agent interaction testing
   - `/tests/integration/test_quantum_consistency.py`: State consistency across boundaries
   - [Continue with integration test coverage]

6. **End-to-End Tests** (18 files, ~1800 LOC)
   - `/tests/e2e/test_requirement_to_deployment.py`: Complete workflow testing
   - `/tests/e2e/test_quantum_convergence.py`: Full convergence cycle testing
   - [Continue with realistic user scenarios]

TESTING REQUIREMENTS:
- Property-based testing for all mathematical functions
- Quantum state consistency validation in all tests
- Comprehensive coverage of agent interactions
- Performance regression testing
- Mathematical property verification

DEPENDENCIES: ALL previous phases (complete system required for testing)
BLOCKS: This validates the entire system implementation
```

---

## PHASE 8: SUPPORTING INFRASTRUCTURE

### Prompt 11: Configuration Management (`/config` - 4 files)

**ELEVENTH STEP**: Implement configuration management system.

```
Implement the configuration management system in `/config`. This manages hierarchical configuration with environment substitution and validation.

REQUIRED FILES (implement ALL 4 files):

1. `/config/__init__.py` (5 LOC)
   - Export ConfigLoader, ConfigValidator

2. `/config/loader.py` (90 LOC)
   - ConfigLoader with YAML support
   - Environment variable substitution ${VAR}
   - Hierarchical configuration merging
   - Schema validation integration

3. `/config/schemas.py` (60 LOC)
   - JSON schemas for configuration validation
   - QuantaCirc-specific configuration schemas
   - Nested schema validation

4. `/config/validator.py` (50 LOC)
   - Configuration validation framework
   - Business rule validation
   - Error reporting and suggestions

DEPENDENCIES: core/types.py
BLOCKS: All components need configuration
```

### Prompt 12: Deployment Infrastructure (`/deployment` - 20+ files)

**TWELFTH STEP**: Implement complete deployment automation.

```
Implement the deployment infrastructure in `/deployment`. This provides cloud-native deployment with infrastructure as code.

REQUIRED STRUCTURE:
1. `/deployment/docker/`: Docker containerization (5 files)
2. `/deployment/k8s/`: Kubernetes manifests (8 files) 
3. `/deployment/helm/`: Helm charts (5 files)
4. `/deployment/terraform/`: Infrastructure as Code (4 files)
5. `/deployment/scripts/`: Deployment scripts (3 files)

IMPLEMENTATION REQUIREMENTS:
- Multi-environment support (dev/staging/prod)
- Quantum state preservation across deployments
- Health checks and monitoring integration
- Security hardening and secrets management

DEPENDENCIES: core/, monitoring/, config/
BLOCKS: Production deployment requires this infrastructure
```

### Prompt 13: Development Tools (`/tools` - 8 files)

**THIRTEENTH STEP**: Implement development tooling for enhanced productivity.

```
Implement development tools in `/tools`. These enhance developer productivity and system maintainability.

REQUIRED FILES (implement ALL 8 files):

1. `/tools/codegen.py` (80 LOC)
   - Code generation from templates
   - Boilerplate reduction
   - Agent code scaffolding

2. `/tools/validator.py` (60 LOC)
   - Configuration and schema validation
   - Mathematical property validation
   - Code quality validation

3. `/tools/profiler.py` (70 LOC)
   - Performance profiling for energy calculations
   - Agent execution profiling
   - Bottleneck identification

4. `/tools/visualizer.py` (90 LOC)
   - Quantum state visualization
   - Energy landscape visualization
   - Agent interaction diagrams

5. `/tools/benchmarks.py` (60 LOC)
   - Performance benchmarking suite
   - Regression testing
   - Comparative analysis

6. `/tools/linter.py` (50 LOC)
   - Custom linting rules for QuantaCirc
   - Mathematical consistency checking
   - Code quality enforcement

7. `/tools/migrate.py` (40 LOC)
   - Schema migration handling
   - Version upgrade automation
   - Data transformation

8. `/tools/inspector.py` (70 LOC)
   - Advanced debugging tools
   - Quantum state inspection
   - Agent behavior analysis

DEPENDENCIES: core/, math/, agents/
BLOCKS: Development workflow enhancement
```

### Prompt 14: Automation Scripts (`/scripts` - 10 files)

**FOURTEENTH STEP**: Implement automation scripts for common tasks.

```
Implement automation scripts in `/scripts`. These automate development, testing, and operational tasks.

REQUIRED FILES (implement ALL 10 files):

1. `/scripts/setup.py` (60 LOC)
   - Development environment setup
   - Dependency installation
   - Initial configuration

2. `/scripts/build.py` (80 LOC)
   - Build system for all components
   - Artifact generation
   - Version management

3. `/scripts/test.py` (70 LOC)
   - Test execution automation
   - Coverage reporting
   - Performance testing

4. `/scripts/deploy/dev.py` (40 LOC)
5. `/scripts/deploy/staging.py` (40 LOC)  
6. `/scripts/deploy/prod.py` (50 LOC)
   - Environment-specific deployment
   - Configuration management
   - Health verification

7. `/scripts/db/migrate.py` (30 LOC)
8. `/scripts/db/backup.py` (30 LOC)
   - Database operations
   - Migration management
   - Backup/restore

9. `/scripts/utils/cleanup.py` (40 LOC)
10. `/scripts/perf/benchmark.py` (50 LOC)
    - Utility and performance scripts
    - System maintenance
    - Benchmarking automation

DEPENDENCIES: All system components
BLOCKS: Operational automation
```

### Prompt 15: Formal Proofs (`/proofs` - 8 files)

**FIFTEENTH STEP**: Implement formal proof system integration.

```
Implement the formal proof system in `/proofs`. This provides mathematical guarantees through formal verification.

REQUIRED FILES (implement ALL 8 files):

1. `/proofs/coq/convergence.v` (200 LOC)
   - Coq proofs for annealing convergence
   - Mathematical theorems
   - Verification automation

2. `/proofs/coq/stability.v` (150 LOC)
   - Lyapunov stability proofs
   - Convergence rate bounds
   - Stability certificates

3. `/proofs/coq/energy.v` (120 LOC)
   - Energy function properties
   - Conservation laws
   - Monotonicity proofs

4. `/proofs/agda/functor.agda` (180 LOC)
   - Category theory functor proofs
   - Composition preservation
   - Identity mapping verification

5. `/proofs/smt/constraints.smt2` (100 LOC)
   - SMT constraint definitions
   - Closure rule formalization
   - Satisfiability checking

6. `/proofs/validators.py` (80 LOC)
   - Proof validation automation
   - Certificate generation
   - Integration with verification pipeline

7. `/proofs/certificates/` (Directory)
   - Generated proof certificates
   - Verification artifacts
   - Mathematical guarantees

8. `/proofs/README.md` (Documentation)
   - Proof system explanation
   - Mathematical foundations
   - Verification procedures

DEPENDENCIES: math/, core/
BLOCKS: Formal verification guarantees
```

### Prompt 16: Artifact Management (`/artifacts` - 6 files)

**SIXTEENTH STEP**: Implement artifact management system.

```
Implement artifact management in `/artifacts`. This handles generated code, templates, and build outputs.

REQUIRED FILES (implement ALL 6 files):

1. `/artifacts/generator.py` (100 LOC)
   - Template-based artifact generation
   - Code scaffolding
   - Configuration file generation

2. `/artifacts/templates/` (Directory structure)
   - Project templates
   - Agent templates
   - Configuration templates

3. `/artifacts/storage.py` (60 LOC)
   - Artifact storage abstraction
   - Version control integration
   - Cleanup management

4. `/artifacts/validator.py` (40 LOC)
   - Artifact validation
   - Integrity checking
   - Quality assurance

5. `/artifacts/registry.py` (50 LOC)
   - Artifact registry
   - Dependency tracking
   - Metadata management

6. `/artifacts/cleanup.py` (30 LOC)
   - Automated cleanup
   - Storage optimization
   - Retention policies

DEPENDENCIES: core/, templates/
BLOCKS: Code generation and artifact management
```

### Prompt 17: Documentation System (`/docs` - 15 files)

**SEVENTEENTH STEP**: Implement comprehensive documentation system.

```
Implement the documentation system in `/docs`. This provides complete system documentation with mathematical specifications.

REQUIRED STRUCTURE:
1. `/docs/api/`: Auto-generated API documentation (5 files)
2. `/docs/math/`: Mathematical specifications (3 files)
3. `/docs/guides/`: User and developer guides (4 files)
4. `/docs/examples/`: Code examples and tutorials (3 files)

KEY DOCUMENTATION FILES:
- `/docs/math/foundations.md`: Complete mathematical foundation
- `/docs/api/core.md`: Core API documentation
- `/docs/guides/user_guide.md`: User guide and tutorials
- `/docs/guides/dev_guide.md`: Developer contribution guide
- `/docs/architecture.md`: System architecture overview

IMPLEMENTATION REQUIREMENTS:
- Mathematical formulations with LaTeX
- Code examples for all APIs
- Interactive tutorials
- Comprehensive coverage of all components

DEPENDENCIES: All system components
BLOCKS: User adoption and contribution
```

---

## PHASE 9: FINAL INTEGRATION & VALIDATION

### Prompt 18: System Integration & Final Validation

**FINAL STEP**: Complete system integration and comprehensive validation.

```
Perform final system integration and validation. This ensures all ~200 files work together as a coherent quantum-mechanical software engineering system.

INTEGRATION CHECKLIST:
1. **Mathematical Consistency**: Verify all mathematical components integrate properly
2. **Agent Coordination**: Test complete agent pipeline with all 10 agents
3. **CLI Functionality**: Validate all CLI commands work end-to-end
4. **Monitoring Integration**: Verify complete observability works
5. **Deployment Pipeline**: Test full deployment automation
6. **Documentation Completeness**: Ensure all components are documented
7. **Performance Validation**: Benchmark system performance
8. **Security Audit**: Complete security review
9. **Formal Verification**: Run complete proof validation
10. **User Acceptance**: Test complete user workflows

FINAL VALIDATION REQUIREMENTS:
- All ~200 files implemented and integrated
- Complete test suite passing (1000+ tests)
- Full mathematical verification
- End-to-end user workflows functional
- Performance benchmarks met
- Security requirements satisfied
- Documentation complete and accurate

SYSTEM READINESS CRITERIA:
- Energy function E_approx correctly computed across all components
- Lyapunov potential Φ properly monitored for stability
- Two-phase annealing algorithm achieving convergence
- All 10 agents operational and coordinated
- CLI providing complete user interface
- Monitoring providing full system observability
- Deployment automation working across environments
- Formal proofs validating mathematical guarantees

Upon completion of this final prompt, the QuantaCirc system will be fully operational as a quantum-mechanical software engineering platform with mathematical rigor, formal verification, and agentic automation.
```

---

## SUMMARY

This comprehensive prompt sequence covers the complete QuantaCirc system implementation:

- **~200+ files** across 15+ directories
- **Rigorous dependency ordering** ensuring proper domino effect
- **Mathematical consistency** throughout all components  
- **Formal verification** integration at every level
- **Complete agent ecosystem** with 10 specialized agents
- **Quantum state awareness** in all system components
- **Production-ready infrastructure** with deployment automation
- **Comprehensive testing** ensuring system reliability

Each prompt builds upon previous implementations, creating an unbreakable chain that results in a complete, mathematically rigorous, quantum-mechanical software engineering system.
