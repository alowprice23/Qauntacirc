# QuantaCirc Lean-Agentic File Map (420 Files)

This document provides a complete file map for the QuantaCirc system, based on the lean-agentic architecture. It includes the path, estimated Lines of Code (LOC), and a brief description for each of the 420 version-controlled files.

---

## Root & Config (18 Files)

| Path                     | Est. LOC | Description                                       |
| ------------------------ | -------- | ------------------------------------------------- |
| `README.md`              | 300      | Project overview, goals, and quick start guide.   |
| `LICENSE`                | 20       | MIT License text.                                 |
| `.gitignore`             | 80       | Standard ignore patterns for Python projects.     |
| `.dockerignore`          | 40       | What to exclude from Docker build context.        |
| `.env.example`           | 25       | Template for environment variables.               |
| `Makefile`               | 100      | Convenience targets for build, test, and deploy.  |
| `pyproject.toml`         | 120      | Python project configuration and dependencies.    |
| `setup.cfg`              | 50       | Configuration for linting and formatting tools.   |
| `quantacirc.yml`         | 60       | Main configuration file for the QuantaCirc system.|
| `quantacirc.schema.json` | 200      | JSON Schema for validating `quantacirc.yml`.    |
| `version.py`             | 5        | Single source of truth for the project version.   |
| `CHANGELOG.md`           | 150      | Human-readable history of changes per release.    |
| `CODE_OF_CONDUCT.md`     | 50       | Code of Conduct for contributors.                 |
| `CONTRIBUTING.md`        | 100      | Guidelines for contributing to the project.       |
| `SECURITY.md`            | 60       | Security policy and vulnerability reporting.      |
| `.pre-commit-config.yaml`| 40       | Configuration for pre-commit hooks.               |
| `.editorconfig`          | 30       | Consistent coding styles across editors.          |
| `.gitattributes`         | 20       | Define attributes for git paths.                  |

---

## CLI (12 Files)

| Path                           | Est. LOC | Description                                                |
| ------------------------------ | -------- | ---------------------------------------------------------- |
| `cli/__init__.py`              | 5        | CLI package initializer.                                   |
| `cli/main.py`                  | 150      | Main `Typer` entry point for all `qc` commands.          |
| `cli/commands/__init__.py`     | 5        | Commands package initializer.                              |
| `cli/commands/init.py`         | 80       | `qc init`: Scaffolds a new QuantaCirc project.             |
| `cli/commands/generate.py`     | 120      | `qc generate`: Runs the agent pipeline for a requirement.    |
| `cli/commands/verify.py`       | 90       | `qc verify`: Runs formal and empirical verification checks.|
| `cli/commands/deploy.py`       | 100      | `qc deploy`: Manages deployment to different environments. |
| `cli/commands/demo.py`         | 70       | `qc demo`: Runs example projects.                          |
| `cli/commands/status.py`       | 60       | `qc status`: Displays the current system state and metrics.|
| `cli/commands/memory.py`       | 80       | `qc memory`: Interacts with the Constellation memory.      |
| `cli/formatters/__init__.py`   | 5        | Formatters package initializer.                            |
| `cli/formatters/table.py`      | 100      | Utility for printing rich tables to the console.           |

---

## Core (22 Files)

| Path                            | Est. LOC | Description                                                               |
| ------------------------------- | -------- | ------------------------------------------------------------------------- |
| `core/__init__.py`              | 5        | Core package initializer.                                                 |
| `core/orchestrator.py`          | 400      | Main loop for the agent pipeline, manages state and tasks.                |
| `core/run_ledger.py`            | 200      | Manages the auditable log of runs, decisions, and artifacts.              |
| `core/energy_calculator.py`     | 350      | Computes the `E_approx` energy function and its components.               |
| `core/closure_rules.py`         | 150      | Manages and applies the `Δ` closure rule set.                             |
| `core/convergence_engine.py`    | 250      | Detects convergence (`λ`, gradient norms) and phase switches.             |
| `core/two_phase_annealer.py`    | 300      | Implements the two-phase annealing optimization algorithm.                |
| `core/functor.py`               | 300      | Implements the `SoftSys` -> `QuantSys` functor (`ρ` computation).       |
| `core/constraint_solver.py`     | 180      | SMT front-end for checking constraint violations.                         |
| `core/error_budget.py`          | 200      | Manages the project's error budget and risk calculations.                 |
| `core/lyapunov_monitor.py`      | 220      | Tracks the `Φ` Lyapunov function and bounded excursions.                |
| `core/state_space.py`           | 150      | Defines the software state space `S` and its transformations.           |
| `core/edit_distance.py`         | 80       | Computes metrics between software states.                                 |
| `core/metrics.py`               | 100      | Core metrics emitters for the system.                                     |
| `core/validators.py`            | 120      | Core validation functions for system integrity.                           |
| `core/exceptions.py`            | 70       | Custom exception types for the core system.                               |
| `core/types.py`                 | 180      | Core Pydantic models and type definitions.                                |
| `core/serialization.py`         | 100      | Serialization and deserialization of core data structures.                |
| `core/persistence.py`           | 130      | Handles persistence of the system state.                                  |
| `core/config_loader.py`         | 90       | Loads and validates the main `quantacirc.yml` configuration.            |
| `core/plugin_registry.py`       | 80       | A simple plugin system for extending core functionality.                  |
| `core/utils.py`                 | 100      | Shared utility functions for the core package.                            |

---

## Agents (40 Files)

| Path                              | Est. LOC | Description                                                              |
| --------------------------------- | -------- | ------------------------------------------------------------------------ |
| `agents/__init__.py`              | 5        | Agent package initializer.                                               |
| `agents/base/__init__.py`         | 5        | Base agent utilities.                                                    |
| `agents/base/agent.py`            | 150      | Abstract base class for all agents.                                      |
| `agents/base/prompts.py`          | 50       | Utilities for managing prompt specs.                                     |
| `agents/base/ops.py`              | 80       | Base operations shared across agents.                                    |
| `agents/base/memory.py`           | 100      | Base interface for interacting with Constellation memory.                |
| `agents/base/metrics.py`          | 60       | Prometheus-style counters and gauges for agents.                         |
| `agents/base/policies.py`         | 70       | Base policy checker for agent actions.                                   |
| `agents/base/contracts.py`        | 90       | Pre/postcondition contract enforcement for agents.                       |
| `agents/base/router.py`           | 120      | Routes tasks to appropriate agents based on type.                        |
| `agents/planck_forge/agent.py`    | 250      | Quantizes requirements into formal tasks.                                  |
| `agents/planck_forge/prompts.py`  | 100      | Prompts for requirement disambiguation and decomposition.                |
| `agents/planck_forge/ops.py`      | 150      | Operations for creating and linking task quanta.                         |
| `agents/schrodinger_dev/agent.py` | 300      | Generates code and proof skeletons from tasks.                           |
| `agents/schrodinger_dev/prompts.py`| 150      | Prompts for code and proof synthesis.                                    |
| `agents/schrodinger_dev/ops.py`   | 200      | Operations for running code generators and proof assistants.             |
| `agents/pauli_guard/agent.py`     | 280      | Enforces orthogonality by detecting and refactoring duplicates.          |
| `agents/pauli_guard/prompts.py`   | 100      | Prompts for generating human-readable refactoring plans.                 |
| `agents/pauli_guard/ops.py`       | 180      | Operations for code similarity analysis and automated refactoring.       |
| `agents/uncertain_ai/agent.py`    | 260      | Manages risk and generates tests to reduce uncertainty.                  |
| `agents/uncertain_ai/prompts.py`  | 120      | Prompts for generating test cases and risk narratives.                   |
| `agents/uncertain_ai/ops.py`      | 160      | Operations for running test generators and computing risk bounds.        |
| `agents/tunnel_fix/agent.py`      | 220      | Optimizes performance bottlenecks.                                       |
| `agents/tunnel_fix/prompts.py`    | 80       | Prompts for suggesting performance improvements.                         |
| `agents/tunnel_fix/ops.py`        | 140      | Operations for performance profiling and patch application.              |
| `agents/bose_boost/agent.py`      | 200      | Manages collective scaling and deployment configurations.                |
| `agents/bose_boost/prompts.py`    | 70       | Prompts for generating deployment strategies.                            |
| `agents/bose_boost/ops.py`        | 130      | Operations for generating Kubernetes manifests and HPA rules.            |
| `agents/phonon_flow/agent.py`     | 210      | Optimizes data flow and communication patterns.                          |
| `agents/phonon_flow/prompts.py`   | 70       | Prompts for explaining data flow optimizations.                          |
| `agents/phonon_flow/ops.py`       | 130      | Operations for graph analysis and telemetry generation.                  |
| `agents/fluctua_test/agent.py`    | 240      | Runs chaos tests to ensure system stability.                             |
| `agents/fluctua_test/prompts.py`  | 90       | Prompts for generating chaos test scenarios.                             |
| `agents/fluctua_test/ops.py`      | 150      | Operations for fault injection and stability analysis.                   |
| `agents/hydro_spread/agent.py`    | 180      | Models and forecasts system growth and complexity.                       |
| `agents/hydro_spread/prompts.py`  | 60       | Prompts for generating growth reports.                                   |
| `agents/hydro_spread/ops.py`      | 110      | Operations for running scaling law simulations.                          |
| `agents/london_link/agent.py`     | 230      | Manages and optimizes external dependencies.                             |
| `agents/london_link/prompts.py`   | 80       | Prompts for explaining dependency changes and CVE mitigations.           |
| `agents/london_link/ops.py`       | 140      | Operations for dependency analysis and SBOM generation.                  |

---

## LLM (14 Files)

| Path                              | Est. LOC | Description                                                        |
| --------------------------------- | -------- | ------------------------------------------------------------------ |
| `llm/__init__.py`                 | 5        | LLM package initializer.                                           |
| `llm/client.py`                   | 150      | Abstract base client for interacting with LLM providers.           |
| `llm/providers/__init__.py`       | 5        | Providers package initializer.                                     |
| `llm/providers/openai_client.py`  | 80       | OpenAI provider implementation.                                    |
| `llm/providers/anthropic_client.py`| 80       | Anthropic provider implementation.                                   |
| `llm/providers/groq_client.py`    | 80       | Groq provider implementation.                                      |
| `llm/providers/gemini_client.py`  | 80       | Google Gemini provider implementation.                             |
| `llm/rate_limiter.py`             | 100      | Rate limiting logic for LLM APIs.                                  |
| `llm/validators.py`               | 90       | Validators for LLM inputs and outputs.                             |
| `llm/retry.py`                    | 70       | Retry logic with exponential backoff for LLM API calls.          |
| `llm/schemas.py`                  | 120      | Pydantic schemas for structured LLM inputs and outputs.          |
| `llm/prompt_registry.py`          | 100      | Registry for managing versioned, checksummed prompts.              |
| `llm/response_parser.py`          | 80       | Parses and cleans LLM responses.                                   |
| `llm/tool_calls.py`               | 110      | Manages the tool calling interface for the LLM.                    |

---

## Math (26 Files)

| Path                              | Est. LOC | Description                                                         |
| --------------------------------- | -------- | ------------------------------------------------------------------- |
| `math/__init__.py`                | 5        | Math package initializer.                                           |
| `math/annealing.py`               | 150      | Simulated annealing utilities.                                      |
| `math/pl_inequality.py`           | 80       | Polyak-Łojasiewicz inequality checks.                               |
| `math/contractive_maps.py`        | 100      | Utilities for working with contractive maps.                        |
| `math/lipschitz.py`               | 70       | Lipschitz constant estimation.                                      |
| `math/info_entropy.py`            | 60       | Shannon entropy calculation.                                        |
| `math/kolmogorov_bounds.py`       | 90       | Bennett-Gács bounded Kolmogorov complexity approximation.         |
| `math/graph_spectra.py`           | 120      | Spectral analysis of graphs.                                        |
| `math/laplacian.py`               | 80       | Graph Laplacian computation.                                        |
| `math/green_kubo.py`              | 70       | Green-Kubo formulas for transport coefficients.                     |
| `math/uncertainty_bounds.py`      | 100      | Chernoff and Hoeffding bounds for risk analysis.                    |
| `math/distance_metrics.py`        | 90       | Metrics for comparing software states.                              |
| `math/lyapunov.py`                | 130      | Lyapunov function utilities.                                        |
| `math/martingales.py`             | 80       | Supermartingale convergence utilities.                              |
| `math/markov_chains.py`           | 100      | Utilities for working with Markov chains.                           |
| `math/random_processes.py`        | 70       | Utilities for stochastic processes.                                 |
| `math/dim_analysis.py`            | 50       | Dimensional analysis checks.                                        |
| `math/units.py`                   | 60       | Unit conversion utilities.                                          |
| `math/samplers.py`                | 90       | Utilities for random sampling.                                      |
| `math/statistics.py`              | 120      | Core statistical functions.                                         |
| `math/distributions.py`           | 100      | Statistical distributions.                                          |
| `math/estimation.py`              | 80       | Parameter estimation utilities.                                     |
| `math/hessian_free.py`            | 110      | Hessian-free optimization utilities.                                |
| `math/line_search.py`             | 70       | Line search algorithms.                                             |
| `math/stopping_rules.py`          | 90       | Stopping criteria for optimization algorithms.                      |
| `math/verification_utils.py`      | 100      | Utilities for verification.                                         |

---

## Messaging (12 Files)

| Path                              | Est. LOC | Description                                                        |
| --------------------------------- | -------- | ------------------------------------------------------------------ |
| `messaging/__init__.py`           | 5        | Messaging package initializer.                                     |
| `messaging/nats_client.py`        | 180      | NATS JetStream client implementation.                              |
| `messaging/publisher.py`          | 80       | Abstracted message publisher.                                      |
| `messaging/subscriber.py`         | 80       | Abstracted message subscriber.                                     |
| `messaging/stream_manager.py`     | 100      | Manages NATS streams.                                              |
| `messaging/topic_manager.py`      | 70       | Manages topic schemas and routing.                                 |
| `messaging/middleware/__init__.py`| 5        | Middleware package initializer.                                    |
| `messaging/middleware/logging.py` | 60       | Middleware for logging messages.                                   |
| `messaging/middleware/metrics.py` | 60       | Middleware for collecting message metrics.                         |
| `messaging/middleware/retry.py`   | 70       | Middleware for retrying failed messages.                           |
| `messaging/middleware/validation.py`| 60       | Middleware for validating message schemas.                         |
| `messaging/serialization.py`      | 90       | Message serialization and compression.                             |

---

## Artifacts (10 Files)

| Path                          | Est. LOC | Description                                                     |
| ----------------------------- | -------- | --------------------------------------------------------------- |
| `artifacts/__init__.py`       | 5        | Artifacts package initializer.                                  |
| `artifacts/generator.py`      | 250      | Main engine for generating files from Jinja2 templates.         |
| `artifacts/storage.py`        | 150      | Abstracted storage layer for artifacts (local, S3, etc.).     |
| `artifacts/file_manager.py`   | 100      | Manages file system artifacts.                                  |
| `artifacts/git_manager.py`    | 120      | Git integration for artifact versioning.                        |
| `artifacts/archive_manager.py`| 80       | Manages archiving of old artifacts.                             |
| `artifacts/cleanup_manager.py`| 70       | Utilities for cleaning up temporary artifacts.                  |
| `artifacts/validators.py`     | 100      | Validators for generated artifacts.                             |
| `artifacts/path_utils.py`     | 60       | Utilities for path manipulation.                                |
| `artifacts/checksums.py`      | 50       | Utilities for calculating artifact checksums.                   |

---

## Monitoring (18 Files)

| Path                              | Est. LOC | Description                                                        |
| --------------------------------- | -------- | ------------------------------------------------------------------ |
| `monitoring/__init__.py`          | 5        | Monitoring package initializer.                                    |
| `monitoring/metrics.py`           | 150      | Core metrics definitions for Prometheus.                           |
| `monitoring/tracing.py`           | 120      | OpenTelemetry tracing setup.                                       |
| `monitoring/logging.py`           | 100      | Structured logging configuration.                                  |
| `monitoring/exporters/__init__.py`| 5        | Exporters package initializer.                                     |
| `monitoring/exporters/prometheus.py`| 80       | Prometheus metrics exporter.                                       |
| `monitoring/exporters/jaeger.py`  | 80       | Jaeger tracing exporter.                                           |
| `monitoring/exporters/elasticsearch.py`| 80       | Elasticsearch log exporter.                                        |
| `monitoring/dashboards/__init__.py`| 5        | Dashboards package initializer.                                    |
| `monitoring/dashboards/grafana.json`| 500      | Grafana dashboard configuration for system metrics.                |
| `monitoring/dashboards/prometheus.yml`| 50       | Prometheus configuration.                                          |
| `monitoring/dashboards/jaeger.yml`| 40       | Jaeger tracing configuration.                                      |
| `monitoring/health/__init__.py`   | 5        | Health check package initializer.                                  |
| `monitoring/health/readiness.py`  | 60       | Kubernetes readiness probe.                                        |
| `monitoring/health/liveness.py`   | 60       | Kubernetes liveness probe.                                         |
| `monitoring/health/dependency.py` | 80       | Health checks for external dependencies.                           |
| `monitoring/anomaly_detector.py`  | 150      | Anomaly detection for system metrics.                              |
| `monitoring/error_tracker.py`     | 100      | Tracks and aggregates system errors.                               |

---

## Deployment (28 Files)

| Path                              | Est. LOC | Description                                                        |
| --------------------------------- | -------- | ------------------------------------------------------------------ |
| `deployment/Dockerfile`           | 80       | Multi-stage Dockerfile for the main application.                   |
| `deployment/Dockerfile.cli`       | 40       | Slim Dockerfile for the CLI.                                       |
| `deployment/helm/Chart.yaml`      | 30       | Helm chart metadata.                                               |
| `deployment/helm/values.yaml`     | 150      | Default Helm values.                                               |
| `deployment/helm/values-dev.yaml` | 50       | Development environment values.                                    |
| `deployment/helm/values-staging.yaml`| 50       | Staging environment values.                                        |
| `deployment/helm/values-prod.yaml`| 50       | Production environment values.                                     |
| `deployment/helm/templates/_helpers.tpl`| 100      | Helm template helpers.                                             |
| `deployment/helm/templates/deployment.yaml`| 120      | Kubernetes deployment template.                                  |
| `deployment/helm/templates/service.yaml`| 50       | Kubernetes service template.                                       |
| `deployment/helm/templates/ingress.yaml`| 60       | Kubernetes ingress template.                                       |
| `deployment/helm/templates/configmap.yaml`| 40       | Kubernetes configmap template.                                     |
| `deployment/helm/templates/secret.yaml`| 40       | Kubernetes secret template.                                        |
| `deployment/helm/templates/hpa.yaml`| 50       | Kubernetes HorizontalPodAutoscaler template.                       |
| `deployment/helm/templates/role.yaml`| 40       | Kubernetes role template.                                          |
| `deployment/helm/templates/rolebinding.yaml`| 40       | Kubernetes role binding template.                                |
| `deployment/helm/templates/serviceaccount.yaml`| 30       | Kubernetes service account template.                             |
| `deployment/terraform/main.tf`    | 200      | Main Terraform configuration for infrastructure.                   |
| `deployment/terraform/variables.tf`| 100      | Terraform variables.                                               |
| `deployment/terraform/outputs.tf` | 50       | Terraform outputs.                                                 |
| `deployment/terraform/providers.tf`| 30       | Terraform provider configuration.                                  |
| `deployment/terraform/modules/quantacirc/variables.tf`| 80       | Variables for the QuantaCirc Terraform module.                     |
| `deployment/terraform/modules/quantacirc/main.tf`| 150      | Main logic for the QuantaCirc Terraform module.                   |
| `deployment/terraform/modules/quantacirc/outputs.tf`| 40       | Outputs for the QuantaCirc Terraform module.                    |
| `deployment/scripts/deploy.sh`    | 100      | Deployment script.                                                 |
| `deployment/scripts/rollback.sh`  | 80       | Rollback script.                                                   |
| `deployment/scripts/health_check.sh`| 70       | Health check script.                                               |
| `deployment/scripts/cleanup.sh`   | 60       | Cleanup script.                                                    |

---

## Proofs (20 Files)

| Path                              | Est. LOC | Description                                                        |
| --------------------------------- | -------- | ------------------------------------------------------------------ |
| `proofs/README.md`                | 50       | Overview of the formal proofs.                                     |
| `proofs/coq/_CoqProject`          | 10       | Coq project configuration.                                         |
| `proofs/coq/Makefile`             | 30       | Makefile for compiling Coq proofs.                                 |
| `proofs/coq/AnnealingTwoPhase.v`  | 400      | Coq proof for two-phase annealing convergence.                     |
| `proofs/coq/FunctorProperties.v`  | 350      | Coq proofs for functor properties.                                 |
| `proofs/coq/PL_Inequality.v`      | 200      | Coq proof for the Polyak-Łojasiewicz inequality.                   |
| `proofs/coq/Contraction.v`        | 150      | Coq proof for contraction properties.                              |
| `proofs/coq/LyapunovMartingale.v` | 250      | Coq proof for Lyapunov supermartingale convergence.                |
| `proofs/coq/ClosureRules.v`       | 300      | Coq proof for closure rule set completeness and termination.       |
| `proofs/coq/InvariantPreservation.v`| 200      | Coq proof for invariant preservation.                              |
| `proofs/agda/ContractLayer.agda`  | 150      | Agda proof for multi-logic contract layer.                         |
| `proofs/smt/energy_constraints.smt2`| 100      | SMT2 script for energy constraints.                                |
| `proofs/smt/type_safety.smt2`     | 80       | SMT2 script for type safety.                                       |
| `proofs/smt/consistency.smt2`     | 70       | SMT2 script for consistency checks.                                |
| `proofs/scripts/compile_coq.sh`   | 30       | Script to compile all Coq proofs.                                  |
| `proofs/scripts/run_smt.sh`       | 30       | Script to run all SMT checks.                                      |
| `proofs/scripts/check_agda.sh`    | 30       | Script to check all Agda proofs.                                   |
| `proofs/certs/AnnealingTwoPhase.vo`| -        | Compiled Coq proof artifact.                                       |
| `proofs/certs/FunctorProperties.vo`| -        | Compiled Coq proof artifact.                                       |
| `proofs/certs/ContractLayer.agdai`| -        | Compiled Agda proof artifact.                                      |

---

## Tests (160 Files)

*Note: This section is heavily condensed. It represents a large number of smaller test files.*

| Path                              | Est. LOC | Description                                                        |
| --------------------------------- | -------- | ------------------------------------------------------------------ |
| `tests/__init__.py`               | 5        | Tests package initializer.                                         |
| `tests/conftest.py`               | 100      | Pytest configuration and fixtures.                                 |
| `tests/unit/core/...` (15 files)    | ~1500    | Unit tests for the core system.                                  |
| `tests/unit/agents/...` (32 files)  | ~3200    | Unit tests for all agents, prompts, and ops.                     |
| `tests/unit/llm/...` (8 files)      | ~800     | Unit tests for the LLM integration.                                |
| `tests/unit/math/...` (17 files)    | ~1700    | Unit tests for the math libraries.                               |
| `tests/unit/messaging/...` (7 files)| ~700     | Unit tests for the messaging system.                             |
| `tests/unit/artifacts/...` (6 files)| ~600     | Unit tests for the artifact management system.                   |
| `tests/unit/monitoring/...` (6 files)| ~600     | Unit tests for the monitoring system.                            |
| `tests/unit/deployment/...` (4 files)| ~400     | Unit tests for the deployment system.                            |
| `tests/property/...` (20 files)   | ~2000    | Property-based tests for core algorithms.                          |
| `tests/integration/...` (25 files)| ~2500    | Integration tests for the complete system.                         |
| `tests/e2e/...` (18 files)          | ~1800    | End-to-end tests for common use cases.                             |
| `tests/proofs/...` (8 files)        | ~800     | Tests for the formal verification harness.                         |

---

## Docs (14 Files)

| Path                              | Est. LOC | Description                                                        |
| --------------------------------- | -------- | ------------------------------------------------------------------ |
| `docs/index.md`                   | 100      | Main documentation page.                                           |
| `docs/getting-started.md`         | 200      | Getting started guide.                                             |
| `docs/cli.md`                     | 150      | CLI command reference.                                             |
| `docs/agents.md`                  | 300      | Documentation for all agents.                                      |
| `docs/core.md`                    | 250      | Documentation for the core system.                                 |
| `docs/llm.md`                     | 200      | Documentation for the LLM integration.                             |
| `docs/math.md`                    | 300      | Documentation for the mathematical foundations.                    |
| `docs/rigor_map.md`               | 100      | Rigor classification for all agents.                               |
| `docs/verification_coverage.md`   | 100      | Verification coverage map.                                         |
| `docs/concepts.md`                | 250      | High-level concepts and philosophy.                                |
| `docs/api.md`                     | 150      | API documentation.                                                 |
| `docs/troubleshooting.md`         | 200      | Troubleshooting guide.                                             |
| `docs/changelog.md`               | -        | (Alias of root CHANGELOG.md)                                       |
| `docs/build_docs.py`              | 80       | Script to build the documentation site.                            |

---

## Scripts (14 Files)

| Path                              | Est. LOC | Description                                                        |
| --------------------------------- | -------- | ------------------------------------------------------------------ |
| `scripts/setup/install.sh`        | 50       | Installation script.                                               |
| `scripts/setup/setup-dev.sh`      | 60       | Development environment setup.                                     |
| `scripts/build/build-all.sh`      | 40       | Build all components.                                              |
| `scripts/build/build-cli.sh`      | 30       | Build the CLI.                                                     |
| `scripts/test/run-tests.sh`       | 40       | Run all tests.                                                     |
| `scripts/test/run-unit.sh`        | 30       | Run unit tests.                                                    |
| `scripts/test/run-integration.sh` | 30       | Run integration tests.                                             |
| `scripts/test/run-e2e.sh`         | 30       | Run end-to-end tests.                                              |
| `scripts/proofs/compile-coq.sh`   | 20       | Compile all Coq proofs.                                            |
| `scripts/proofs/check-agda.sh`    | 20       | Check all Agda proofs.                                             |
| `scripts/proofs/run-smt.sh`       | 20       | Run all SMT checks.                                                |
| `scripts/deploy/deploy.sh`        | 80       | Deployment script.                                                 |
| `scripts/deploy/rollback.sh`      | 60       | Rollback script.                                                   |
| `scripts/format/lint-format.sh`   | 40       | Lint and format all code.                                          |

---

## Tools (12 Files)

| Path                              | Est. LOC | Description                                                        |
| --------------------------------- | -------- | ------------------------------------------------------------------ |
| `tools/__init__.py`               | 5        | Tools package initializer.                                         |
| `tools/quantum_debugger.py`       | 200      | Debugger for the quantum state.                                    |
| `tools/wavefunction_visualizer.py`| 150      | Visualizer for the wavefunction.                                   |
| `tools/energy_plotter.py`         | 120      | Plotter for the energy spectrum.                                   |
| `tools/closure_analyzer.py`       | 180      | Analyzer for the closure rule set.                                 |
| `tools/agent_monitor.py`          | 200      | Monitor for agent performance.                                     |
| `tools/performance_analyzer.py`   | 150      | Analyzer for system performance.                                   |
| `tools/dependency_tracker.py`     | 120      | Tracker for external dependencies.                                 |
| `tools/health_dashboard.py`       | 180      | Health dashboard for the system.                                   |
| `tools/llm_tester.py`             | 200      | Tester for the LLM integration.                                    |
| `tools/prompt_validator.py`       | 120      | Validator for LLM prompts.                                         |
| `tools/benchmark_runner.py`       | 150      | Runner for system benchmarks.                                      |
