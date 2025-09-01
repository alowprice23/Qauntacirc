# QuantaCirc Design Prompts

## Essential Prompts for Agentic Software Engineer to Design QuantaCirc

The following prompts represent the minimum set necessary to design the complete QuantaCirc system - an agentic software engineering platform based on quantum mechanical principles.

---

## 1. System Architecture & Mathematical Foundation

**Prompt 1: Core Mathematical Framework**
```
Design the mathematical foundation for QuantaCirc, a quantum-mechanical approach to software engineering. Implement:

1. Energy function E_approx = E_static + E_dynamic + E_interaction that measures software system "energy"
2. Lyapunov potential Φ(S_t) that ensures system stability and convergence
3. Two-phase annealing algorithm with proven convergence properties
4. SoftSys -> QuantSys functor (ρ computation) mapping software to quantum states
5. Closure rules Δ for maintaining system consistency

Create the complete mathematical specification with formulas, proofs, and computational algorithms. This forms the theoretical backbone of the entire system.
```

**Prompt 2: Core Type System & Data Architecture**
```
Design the complete type system for QuantaCirc using Pydantic models. Create:

1. QCState: Core software system state representation
2. EnergyComponents: Static, dynamic, and interaction energy components
3. AgentTask/AgentResult: Communication protocols between agents
4. LyapunovResult: Stability and convergence metrics
5. StateTransformation: Mathematical operations on system states
6. ConstraintViolation: Formal constraint checking results

Ensure all types have validation, serialization, and are mathematically consistent. This becomes the data architecture foundation for the entire system.
```

---

## 2. Core Infrastructure Layer

**Prompt 3: Energy Calculator Engine**
```
Implement the core energy calculation engine that computes E_approx for any software system state. Features required:

1. E_static: Code complexity, coupling, cohesion metrics
2. E_dynamic: Runtime performance, memory usage patterns  
3. E_interaction: Inter-module dependencies, API surface areas
4. Incremental computation for efficiency
5. Energy gradients and Hessians for optimization
6. Caching strategy with invalidation

This engine drives all optimization decisions and must be mathematically rigorous and computationally efficient.
```

**Prompt 4: Orchestrator & Control Loop**
```
Design the central orchestrator that manages the 10 specialized agents in a perfect closed loop. Requirements:

1. Asynchronous agent communication via NATS messaging
2. State machine: IDLE -> PLANNING -> GENERATING -> VERIFYING -> CONVERGED
3. Gate stack validation for all state transitions
4. Energy-based decision making using E_approx
5. Deadlock/livelock prevention with timeout mechanisms
6. Complete audit trail of all decisions

The orchestrator is the "brain" coordinating all system components based on mathematical principles.
```

**Prompt 5: Two-Phase Annealing Optimizer**
```
Implement the two-phase simulated annealing algorithm with mathematical guarantees:

1. Phase A (Exploration): High temperature, broad search, diverse proposals
2. Phase B (Exploitation): Low temperature, local search, refinement  
3. Adaptive temperature schedule based on acceptance rates
4. Convergence detection using λ < 1 contraction factor
5. Lyapunov-guided transitions between phases
6. Global minimum convergence proof

This optimizer must be provably convergent and form the optimization core of the system.
```

---

## 3. Agent Architecture & Specialization

**Prompt 6: Agent Communication Framework**
```
Design the complete agent communication system supporting 10 specialized agents:

1. NATS-based pub/sub messaging with topics per agent
2. AgentTask serialization/deserialization protocols
3. Result aggregation and consensus mechanisms
4. Agent health monitoring and failure recovery
5. Load balancing and task distribution
6. Agent capability registration and discovery

Each agent operates independently but coordinates through this messaging layer.
```

**Prompt 7: Specialized Agent Implementations**
```
Implement the 10 specialized agents that form the core of QuantaCirc:

1. **PlanckForge**: Requirements analysis and architectural planning
2. **PauliGuard**: Security analysis and vulnerability detection
3. **HeisenbergLens**: Code quality analysis and optimization suggestions
4. **SchrodingerTest**: Test generation and execution management
5. **BohrDoc**: Documentation generation and maintenance
6. **DiracDeploy**: Deployment orchestration and infrastructure
7. **MaxwellMonitor**: System monitoring and observability
8. **EinsteinRefactor**: Code refactoring and technical debt management
9. **FermiDebug**: Debugging and issue resolution
10. **NewtonIntegrate**: Integration testing and validation

Each agent must implement the AgentInterface and specialize in its domain while contributing to the overall energy minimization goal.
```

---

## 4. Formal Verification & Constraint System

**Prompt 8: Constraint Solver & Closure Rules**
```
Implement the formal verification system using SMT (Satisfiability Modulo Theories):

1. Closure rules Δ that prevent invalid state transitions
2. Z3-based constraint solver integration
3. Incremental constraint solving for efficiency
4. Proof certificate generation for auditability
5. Unsatisfiable core extraction for debugging
6. Custom constraint types for software engineering domains

This system provides the "irrefutability" guarantee by formally verifying all system changes.
```

**Prompt 9: Stability Monitor & Convergence Detection**
```
Create the Lyapunov monitoring system that ensures mathematical stability:

1. Φ(S_t) computation for any system state S_t
2. Bounded excursion tracking with martingale properties
3. Convergence prediction using contraction analysis
4. Phase transition triggers for the annealing algorithm
5. Stability violation detection and recovery
6. Mathematical convergence certificates

This monitor provides mathematical guarantees about system behavior and convergence.
```

---

## 5. Integration & System Services

**Prompt 10: Persistence & State Management**
```
Design the complete persistence layer with ACID properties:

1. SQLite-based state storage with atomic operations
2. State snapshots with incremental updates
3. Run ledger with cryptographic integrity (blockchain-like)
4. Query interface for analytics and debugging
5. Automatic recovery from corruption or crashes
6. Configuration management with environment substitution

This layer ensures data durability and provides the system's "memory" across runs.
```

**Prompt 11: CLI & User Interface**
```
Create the command-line interface that exposes QuantaCirc functionality:

1. Project initialization and configuration
2. Interactive optimization sessions with real-time feedback
3. Agent management (start/stop/status/logs)
4. State inspection and manipulation commands
5. Energy visualization and convergence tracking
6. Integration with existing development workflows

The CLI should be intuitive yet powerful, suitable for both interactive use and automation.
```

**Prompt 12: Monitoring & Observability**
```
Implement comprehensive system observability:

1. Prometheus metrics for energy, convergence, and performance
2. Structured logging with correlation IDs
3. OpenTelemetry tracing for distributed operations
4. Mathematical metric dashboards (energy landscapes, convergence plots)
5. Agent health and performance monitoring
6. Alert system for stability violations

This provides complete visibility into system behavior and mathematical properties.
```

---

## 6. Testing & Quality Assurance

**Prompt 13: Test Framework & Mathematical Verification**
```
Design the complete testing framework with mathematical rigor:

1. Unit tests for all mathematical functions with property-based testing
2. Integration tests for agent communication and orchestration
3. Convergence tests that verify mathematical guarantees
4. Performance benchmarks for energy computation and optimization
5. Chaos engineering tests for resilience
6. Formal verification tests for constraint solver correctness

Testing must verify both functional correctness and mathematical properties.
```

**Prompt 14: Documentation & Knowledge Management**
```
Create comprehensive documentation system:

1. Mathematical specification with proofs and theorems
2. API documentation with examples and use cases
3. Agent-specific documentation for each specialized agent
4. Tutorial and getting-started guides
5. Architecture decision records (ADRs)
6. Troubleshooting guides and FAQ

Documentation should serve both users and contributors, with clear explanations of the mathematical foundation.
```

---

## 7. Deployment & Operations

**Prompt 15: Deployment & Infrastructure**
```
Design the complete deployment and infrastructure automation:

1. Docker containerization for all components
2. Kubernetes manifests for orchestration
3. Helm charts for configuration management
4. CI/CD pipeline with automated testing and deployment
5. Infrastructure as Code (Terraform) for cloud resources
6. Security hardening and secrets management

The deployment should be cloud-native and support multiple environments (dev/staging/prod).
```

---

## Summary

These 15 prompts represent the minimum viable set needed to design and implement the complete QuantaCirc system. Each prompt builds upon previous ones and covers a critical aspect:

- **Prompts 1-2**: Mathematical foundation and type system
- **Prompts 3-5**: Core computation engines  
- **Prompts 6-7**: Agent architecture and specialization
- **Prompts 8-9**: Formal verification and stability
- **Prompts 10-12**: Integration and system services
- **Prompts 13-14**: Quality assurance and documentation
- **Prompt 15**: Deployment and operations

The agentic engineer should work through these prompts sequentially, as each builds upon the artifacts created in previous prompts. The result will be a complete, mathematically rigorous, and production-ready QuantaCirc system.

Each prompt is designed to be comprehensive enough to guide implementation while being specific enough to ensure correctness and consistency with the overall system architecture.
