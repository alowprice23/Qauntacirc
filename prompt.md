# QuantaCirc Design Prompts

## Directory-Based Prompts for Agentic Software Engineer to Design QuantaCirc

The following prompts are organized by the project directory structure, representing the minimum set necessary to design the complete QuantaCirc system - an agentic software engineering platform based on quantum mechanical principles.

---

## 1. `/core` - Mathematical Foundation & Core Infrastructure

**Prompt 1: Core Mathematical Framework (`/core`)**
```
Design the mathematical foundation for the `core/` directory of QuantaCirc. Implement:

1. **Energy Calculator** (`energy_calculator.py`): E_approx = E_static + E_dynamic + E_interaction
2. **Lyapunov Monitor** (`lyapunov_monitor.py`): Φ(S_t) stability tracking with bounded excursions
3. **Two-Phase Annealer** (`two_phase_annealer.py`): Convergent optimization algorithm
4. **Functor** (`functor.py`): SoftSys -> QuantSys mapping (ρ computation) 
5. **Orchestrator** (`orchestrator.py`): Central control loop managing all agents
6. **State Space** (`state_space.py`): Software state representation and transformations
7. **Constraint Solver** (`constraint_solver.py`): SMT-based formal verification
8. **Types** (`types.py`): Complete Pydantic data architecture
9. **Closure Rules** (`closure_rules.py`): Δ consistency rules

This forms the mathematical and computational heart of the entire system.
```

---

## 2. `/agents` - Specialized Agent Implementations

**Prompt 2: Specialized Agent Architecture (`/agents`)**
```
Implement the 10 specialized agents in the `/agents` directory:

1. **PlanckForge** (`planck_forge.py`): Requirements analysis and architectural planning
2. **PauliGuard** (`pauli_guard.py`): Security analysis and vulnerability detection
3. **HeisenbergLens** (`heisenberg_lens.py`): Code quality analysis and optimization
4. **SchrodingerTest** (`schrodinger_test.py`): Test generation and execution
5. **BohrDoc** (`bohr_doc.py`): Documentation generation and maintenance
6. **DiracDeploy** (`dirac_deploy.py`): Deployment orchestration
7. **MaxwellMonitor** (`maxwell_monitor.py`): System monitoring and observability
8. **EinsteinRefactor** (`einstein_refactor.py`): Code refactoring and technical debt
9. **FermiDebug** (`fermi_debug.py`): Debugging and issue resolution
10. **NewtonIntegrate** (`newton_integrate.py`): Integration testing and validation

Plus shared infrastructure:
- **Agent Base** (`agent_base.py`): Common agent interface and utilities
- **Agent Registry** (`agent_registry.py`): Agent discovery and management

Each agent contributes to overall system energy minimization while specializing in its domain.
```

---

## 3. `/math` - Mathematical Utilities

**Prompt 3: Mathematical Utilities (`/math`)**
```
Create the mathematical utility library for the `/math` directory:

1. **Quantum Mechanics** (`quantum.py`): Quantum state operations, density matrices, unitaries
2. **Annealing** (`annealing.py`): Simulated annealing algorithms and temperature schedules
3. **Lyapunov** (`lyapunov.py`): Lyapunov function analysis and stability theory
4. **Linear Algebra** (`linalg.py`): Optimized matrix operations and decompositions
5. **Optimization** (`optimization.py`): Gradient descent, Newton methods, convergence analysis
6. **Statistics** (`statistics.py`): Statistical analysis, hypothesis testing, distributions
7. **Graph Theory** (`graphs.py`): Dependency graphs, shortest paths, connectivity analysis
8. **Numerical Methods** (`numerical.py`): Integration, differentiation, root finding

These utilities support the mathematical rigor required throughout the system.
```

---

## 4. `/messaging` - Communication Infrastructure  

**Prompt 4: Messaging System (`/messaging`)**
```
Design the communication infrastructure in the `/messaging` directory:

1. **NATS Client** (`nats_client.py`): Pub/sub messaging with agent-specific topics
2. **Message Protocols** (`protocols.py`): AgentTask/AgentResult serialization protocols  
3. **Message Router** (`router.py`): Intelligent message routing and load balancing
4. **Health Monitor** (`health.py`): Agent health monitoring and failure recovery
5. **Message Broker** (`broker.py`): High-level messaging abstractions
6. **Event Bus** (`events.py`): System-wide event distribution
7. **Message Queue** (`queue.py`): Reliable message queuing with persistence

This enables decoupled, asynchronous communication between all system components.
```

---

## 5. `/cli` - Command Line Interface

**Prompt 5: CLI Implementation (`/cli`)**
```
Create a comprehensive CLI in the `/cli` directory:

1. **Main CLI** (`main.py`): Primary command-line interface entry point
2. **Project Commands** (`project.py`): Initialize, configure, manage projects  
3. **Agent Commands** (`agents.py`): Start/stop/status/logs for all agents
4. **State Commands** (`state.py`): Inspect and manipulate system state
5. **Energy Commands** (`energy.py`): Visualize energy landscapes and convergence
6. **Config Commands** (`config.py`): Configuration management and validation
7. **Debug Commands** (`debug.py`): Debugging tools and diagnostics
8. **Interactive Shell** (`shell.py`): REPL for advanced users

The CLI should be intuitive for daily use yet powerful for automation and advanced scenarios.
```

---

## 6. `/monitoring` - Observability & Metrics

**Prompt 6: Monitoring System (`/monitoring`)**
```
Implement comprehensive observability in the `/monitoring` directory:

1. **Metrics Collector** (`metrics.py`): Prometheus-compatible metrics emission
2. **Logger** (`logger.py`): Structured logging with correlation IDs
3. **Tracer** (`tracer.py`): OpenTelemetry distributed tracing
4. **Dashboard** (`dashboard.py`): Mathematical metric visualization (energy, convergence)
5. **Alerting** (`alerts.py`): Alert system for stability violations and errors
6. **Health Checker** (`health_checker.py`): System health monitoring
7. **Performance Monitor** (`performance.py`): Performance profiling and benchmarking

This provides complete visibility into system behavior and mathematical properties.
```

---

## 7. `/tests` - Testing Framework

**Prompt 7: Test Framework (`/tests`)**
```
Design comprehensive testing in the `/tests` directory:

1. **Unit Tests** (`test_core/`): Test all core mathematical functions with property-based testing
2. **Agent Tests** (`test_agents/`): Test individual agent implementations
3. **Integration Tests** (`test_integration/`): Test agent communication and orchestration
4. **Mathematical Tests** (`test_math/`): Verify mathematical guarantees and convergence properties
5. **Performance Tests** (`test_performance/`): Benchmark energy computation and optimization
6. **Chaos Tests** (`test_chaos/`): Resilience and fault injection testing
7. **Fixtures** (`fixtures/`): Test data and mock objects
8. **Test Utilities** (`utils.py`): Testing helpers and assertions

Testing must verify both functional correctness and mathematical properties.
```

---

## 8. `/docs` - Documentation System

**Prompt 8: Documentation (`/docs`)**
```
Create comprehensive documentation in the `/docs` directory:

1. **Mathematical Specification** (`math_spec.md`): Complete mathematical foundation with proofs
2. **Architecture Guide** (`architecture.md`): System architecture and design patterns
3. **API Reference** (`api/`): Auto-generated API documentation
4. **Agent Documentation** (`agents/`): Detailed documentation for each specialized agent
5. **User Guide** (`user_guide.md`): Tutorial and getting-started guides
6. **Developer Guide** (`dev_guide.md`): Contributing guidelines and development setup
7. **ADRs** (`decisions/`): Architecture decision records
8. **FAQ** (`faq.md`): Troubleshooting and frequently asked questions

Documentation should serve both users and contributors with clear mathematical explanations.
```

---

## 9. `/tools` - Development Tools

**Prompt 9: Development Tools (`/tools`)**
```
Implement development tooling in the `/tools` directory:

1. **Code Generator** (`codegen.py`): Generate boilerplate code from templates
2. **Schema Validator** (`validator.py`): Validate configuration and data schemas
3. **Performance Profiler** (`profiler.py`): Profile energy calculations and optimization
4. **State Visualizer** (`visualizer.py`): Visualize system states and energy landscapes
5. **Benchmark Runner** (`benchmarks.py`): Standardized performance benchmarks
6. **Linter** (`linter.py`): Custom linting rules for QuantaCirc code
7. **Migration Tool** (`migrate.py`): Handle schema migrations and upgrades
8. **Debug Inspector** (`inspector.py`): Advanced debugging and inspection tools

These tools enhance developer productivity and system maintainability.
```

---

## 10. `/config` - Configuration Management

**Prompt 10: Configuration System (`/config`)**
```
Design configuration management for the `/config` directory:

1. **Config Loader** (`loader.py`): Load and merge configuration from multiple sources
2. **Schema Definitions** (`schemas.py`): JSON schemas for configuration validation
3. **Environment Handler** (`environment.py`): Environment-specific configuration
4. **Default Configs** (`defaults/`): Default configuration templates
5. **Config Validator** (`validator.py`): Comprehensive configuration validation
6. **Secret Manager** (`secrets.py`): Secure handling of sensitive configuration
7. **Override System** (`overrides.py`): Configuration override mechanisms

Support hierarchical configuration with environment substitution and validation.
```

---

## 11. `/deployment` - Infrastructure & Deployment

**Prompt 11: Deployment Infrastructure (`/deployment`)**
```
Create deployment automation in the `/deployment` directory:

1. **Docker** (`docker/`): Containerization for all components
2. **Kubernetes** (`k8s/`): Kubernetes manifests and operators
3. **Helm Charts** (`helm/`): Parameterized deployment templates
4. **Terraform** (`terraform/`): Infrastructure as Code
5. **CI/CD Pipelines** (`pipelines/`): Automated testing and deployment
6. **Security** (`security/`): Security hardening and secrets management
7. **Monitoring** (`monitoring/`): Deployment-specific monitoring setup

Support cloud-native deployment across multiple environments (dev/staging/prod).
```

---

## 12. `/proofs` - Mathematical Proofs

**Prompt 12: Mathematical Proofs (`/proofs`)**
```
Document formal proofs in the `/proofs` directory:

1. **Convergence Proofs** (`convergence.md`): Prove two-phase annealing convergence
2. **Stability Proofs** (`stability.md`): Prove Lyapunov stability guarantees
3. **Correctness Proofs** (`correctness.md`): Prove system correctness properties
4. **Energy Function Proofs** (`energy.md`): Prove energy function properties
5. **Functor Proofs** (`functor.md`): Prove SoftSys -> QuantSys functor properties
6. **Constraint Proofs** (`constraints.md`): Prove closure rule completeness
7. **Security Proofs** (`security.md`): Prove security properties

These proofs provide the mathematical foundation for the "irrefutability" guarantee.
```

---

## 13. `/scripts` - Automation Scripts

**Prompt 13: Automation Scripts (`/scripts`)**
```
Create automation scripts in the `/scripts` directory:

1. **Setup Script** (`setup.py`): Development environment setup
2. **Build Script** (`build.py`): Build system for all components
3. **Test Runner** (`test.py`): Comprehensive test execution
4. **Deployment Scripts** (`deploy/`): Deployment automation
5. **Database Scripts** (`db/`): Database migration and management
6. **Utility Scripts** (`utils/`): Various utility and maintenance scripts
7. **Performance Scripts** (`perf/`): Performance testing and profiling

These scripts automate common development and operational tasks.
```

---

## 14. `/llm` - LLM Integration

**Prompt 14: LLM Integration (`/llm`)**
```
Design LLM integration capabilities in the `/llm` directory:

1. **LLM Client** (`client.py`): Interface to various LLM providers
2. **Prompt Templates** (`templates/`): Structured prompts for different agent tasks
3. **Context Manager** (`context.py`): Manage conversation context and memory
4. **Response Parser** (`parser.py`): Parse and validate LLM responses
5. **Fine-tuning** (`finetune.py`): Fine-tune models for specific agent tasks
6. **Embedding Engine** (`embeddings.py`): Generate and manage embeddings
7. **Retrieval System** (`retrieval.py`): RAG implementation for knowledge access

This enables agents to leverage LLMs while maintaining mathematical rigor.
```

---

## 15. `/artifacts` - Build Artifacts & Output

**Prompt 15: Artifacts Management (`/artifacts`)**
```
Design artifact management for the `/artifacts` directory:

1. **Build Artifacts** (`builds/`): Compiled binaries and packages  
2. **Generated Code** (`generated/`): Auto-generated code and schemas
3. **Reports** (`reports/`): Test reports, coverage, and analysis
4. **Documentation** (`docs/`): Generated documentation artifacts
5. **Metrics** (`metrics/`): Historical performance and convergence data
6. **Proofs** (`proofs/`): Generated proof certificates and verification results
7. **Backups** (`backups/`): State backups and recovery artifacts

This provides organized storage for all system outputs and generated content.
```

---

## Summary

These 15 directory-based prompts provide complete coverage of the QuantaCirc system:

1. **`/core`** - Mathematical foundation and core infrastructure
2. **`/agents`** - Specialized agent implementations  
3. **`/math`** - Mathematical utilities and algorithms
4. **`/messaging`** - Communication infrastructure
5. **`/cli`** - Command-line interface
6. **`/monitoring`** - Observability and metrics
7. **`/tests`** - Testing framework
8. **`/docs`** - Documentation system
9. **`/tools`** - Development tools
10. **`/config`** - Configuration management
11. **`/deployment`** - Infrastructure and deployment
12. **`/proofs`** - Mathematical proofs
13. **`/scripts`** - Automation scripts
14. **`/llm`** - LLM integration
15. **`/artifacts`** - Build artifacts and output

Each prompt corresponds directly to the project directory structure, making implementation straightforward and ensuring nothing is overlooked. The agentic engineer can work through these directory by directory, building a complete, mathematically rigorous, and production-ready QuantaCirc system.
