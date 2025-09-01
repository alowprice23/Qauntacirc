# Plan for the `monitoring` Directory - Complete Implementation Guide

## 1. Architecture Overview & Philosophy

The `monitoring` directory implements comprehensive observability for QuantaCirc, providing real-time insights into system performance, quantum state evolution, and agent behavior. This package integrates Prometheus metrics, OpenTelemetry tracing, structured logging, and custom anomaly detection to ensure complete system visibility while maintaining quantum-mechanical consistency.

### Core Design Principles

1. **Quantum State Observability**: Metrics capture the evolution of energy functions and Lyapunov potentials
2. **Multi-Dimensional Monitoring**: Metrics, traces, logs, and health checks provide complete system visibility
3. **Predictive Analytics**: Machine learning-based anomaly detection for proactive issue identification
4. **Performance Optimization**: Low-overhead monitoring that doesn't impact system performance
5. **Standards Compliance**: OpenTelemetry and Prometheus standards for interoperability
6. **Real-Time Alerting**: Immediate notification of critical system state changes

### Mathematical Integration

Monitoring captures quantum-mechanical system properties:
- **Energy Function Tracking**: Real-time monitoring of E_approx and its components
- **Lyapunov Stability Metrics**: Continuous tracking of Φ and convergence indicators
- **Phase Transition Detection**: Automated detection of optimization phase changes
- **Convergence Monitoring**: Real-time λ tracking and convergence prediction
- **Closure Rule Violations**: Immediate alerts for Δ constraint violations

---

## 2. Core Infrastructure Files

### File: `monitoring/__init__.py` (5 LOC)

**Purpose**: Package initializer exposing primary monitoring interfaces and utilities.

**Implementation**:
```python
"""
QuantaCirc Monitoring Infrastructure
==================================

Comprehensive observability system providing metrics, tracing, logging,
and health monitoring for the quantum-mechanical software engineering system.
"""

from .metrics import QuantumMetrics, MetricsCollector
from .tracing import QuantumTracer, TraceManager
from .logging import StructuredLogger
from .anomaly_detector import AnomalyDetector

__all__ = ["QuantumMetrics", "MetricsCollector", "QuantumTracer", "TraceManager", 
           "StructuredLogger", "AnomalyDetector"]
```

**Integration Points**:
- Used by all system components for observability
- Imported by CLI for monitoring commands
- Referenced by deployment for health checks

---

### File: `monitoring/metrics.py` (150 LOC)

**Purpose**: Core Prometheus metrics collection with quantum-specific measurements and mathematical state tracking.

**Core Functionality**:
- Quantum state metrics (energy, Lyapunov, phase)
- Agent performance and behavior tracking
- System resource utilization monitoring
- Mathematical convergence indicators
- Custom histogram and gauge implementations

**Implementation Strategy**:
```python
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry
from typing import Dict, Any, Optional, List
import time
from dataclasses import dataclass
from enum import Enum
import numpy as np

from core.types import QCState, AgentResult

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    INFO = "info"

@dataclass
class MetricDefinition:
    """Definition of a quantum system metric."""
    name: str
    metric_type: MetricType
    help_text: str
    labels: List[str] = None
    buckets: List[float] = None  # For histograms

class QuantumMetrics:
    """
    Prometheus metrics collection for QuantaCirc quantum system.
    
    Provides specialized metrics for tracking quantum mechanical properties,
    agent behavior, and system performance with mathematical rigor.
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self.metrics: Dict[str, Any] = {}
        self._initialize_core_metrics()
    
    def _initialize_core_metrics(self):
        """Initialize core quantum system metrics."""
        
        # Quantum State Metrics
        self.energy_gauge = Gauge(
            'quantacirc_energy_total',
            'Total system energy (E_approx)',
            ['component'],  # static, dynamic, interaction
            registry=self.registry
        )
        
        self.energy_components_gauge = Gauge(
            'quantacirc_energy_components',
            'Individual energy components',
            ['component'],
            registry=self.registry
        )
        
        self.lyapunov_gauge = Gauge(
            'quantacirc_lyapunov_potential',
            'Lyapunov potential for stability analysis',
            registry=self.registry
        )
        
        self.contraction_factor_gauge = Gauge(
            'quantacirc_contraction_factor',
            'Contraction factor lambda for convergence',
            registry=self.registry
        )
        
        self.optimization_phase_info = Info(
            'quantacirc_optimization_phase',
            'Current optimization phase (A=exploration, B=exploitation)',
            registry=self.registry
        )
        
        # Agent Performance Metrics
        self.agent_executions_counter = Counter(
            'quantacirc_agent_executions_total',
            'Total number of agent executions',
            ['agent_name', 'result'],  # result: success, failure, skipped
            registry=self.registry
        )
        
        self.agent_execution_duration = Histogram(
            'quantacirc_agent_execution_duration_seconds',
            'Time spent in agent execution',
            ['agent_name'],
            buckets=[0.001, 0.01, 0.1, 1.0, 10.0, 60.0, 300.0],
            registry=self.registry
        )
        
        self.agent_proposals_counter = Counter(
            'quantacirc_agent_proposals_total',
            'Number of proposals generated by agents',
            ['agent_name', 'accepted'],
            registry=self.registry
        )
        
        self.agent_energy_impact = Histogram(
            'quantacirc_agent_energy_impact',
            'Energy change caused by agent actions',
            ['agent_name', 'component'],
            buckets=[-10.0, -1.0, -0.1, -0.01, 0, 0.01, 0.1, 1.0, 10.0],
            registry=self.registry
        )
        
        # System Performance Metrics
        self.messages_processed_counter = Counter(
            'quantacirc_messages_processed_total',
            'Total number of messages processed',
            ['topic', 'status'],  # status: success, error, timeout
            registry=self.registry
        )
        
        self.message_processing_duration = Histogram(
            'quantacirc_message_processing_duration_seconds',
            'Time spent processing messages',
            ['topic'],
            registry=self.registry
        )
        
        self.llm_requests_counter = Counter(
            'quantacirc_llm_requests_total',
            'Total LLM requests',
            ['provider', 'model', 'status'],
            registry=self.registry
        )
        
        self.llm_token_usage = Histogram(
            'quantacirc_llm_tokens_used',
            'Tokens used per LLM request',
            ['provider', 'model', 'type'],  # type: prompt, completion
            buckets=[10, 50, 100, 500, 1000, 5000, 10000, 50000],
            registry=self.registry
        )
        
        self.llm_cost_gauge = Gauge(
            'quantacirc_llm_cost_usd',
            'Estimated LLM costs in USD',
            ['provider', 'model'],
            registry=self.registry
        )
        
        # Mathematical Convergence Metrics
        self.convergence_rate_gauge = Gauge(
            'quantacirc_convergence_rate',
            'Current convergence rate estimate',
            registry=self.registry
        )
        
        self.closure_violations_counter = Counter(
            'quantacirc_closure_violations_total',
            'Number of closure rule violations',
            ['rule_type'],
            registry=self.registry
        )
        
        self.verification_results_counter = Counter(
            'quantacirc_verification_results_total',
            'Results of formal verification checks',
            ['verification_type', 'result'],  # result: pass, fail, timeout
            registry=self.registry
        )
        
        # System Resource Metrics
        self.cpu_usage_gauge = Gauge(
            'quantacirc_cpu_usage_percent',
            'CPU usage percentage',
            ['component'],
            registry=self.registry
        )
        
        self.memory_usage_gauge = Gauge(
            'quantacirc_memory_usage_bytes',
            'Memory usage in bytes',
            ['component', 'type'],  # type: heap, stack, cache
            registry=self.registry
        )
        
        self.active_connections_gauge = Gauge(
            'quantacirc_active_connections',
            'Number of active connections',
            ['connection_type'],  # nats, database, llm_provider
            registry=self.registry
        )
    
    def record_quantum_state(self, state: QCState):
        """Record quantum state measurements."""
        
        # Update energy metrics
        self.energy_gauge.labels(component='total').set(state.energy)
        
        if hasattr(state, 'energy_components'):
            components = state.energy_components
            self.energy_components_gauge.labels(component='static').set(components.static)
            self.energy_components_gauge.labels(component='dynamic').set(components.dynamic)
            self.energy_components_gauge.labels(component='interaction').set(components.interaction)
        
        # Update stability metrics
        if hasattr(state, 'lyapunov_potential'):
            self.lyapunov_gauge.set(state.lyapunov_potential)
        
        if hasattr(state, 'contraction_factor'):
            self.contraction_factor_gauge.set(state.contraction_factor)
        
        # Update phase information
        if hasattr(state, 'optimization_phase'):
            self.optimization_phase_info.info({
                'phase': state.optimization_phase,
                'timestamp': state.timestamp.isoformat()
            })
    
    def record_agent_execution(self, 
                              agent_name: str, 
                              result: AgentResult, 
                              duration: float):
        """Record agent execution metrics."""
        
        # Count execution
        status = 'success' if result.action_taken else 'failure' if result.error else 'skipped'
        self.agent_executions_counter.labels(agent_name=agent_name, result=status).inc()
        
        # Record duration
        self.agent_execution_duration.labels(agent_name=agent_name).observe(duration)
        
        # Record energy impact if available
        if hasattr(result, 'energy_delta') and result.energy_delta:
            for component, delta in result.energy_delta.items():
                self.agent_energy_impact.labels(
                    agent_name=agent_name, 
                    component=component
                ).observe(delta)
        
        # Record proposals
        if hasattr(result, 'proposal_generated'):
            accepted = 'true' if result.action_taken else 'false'
            self.agent_proposals_counter.labels(
                agent_name=agent_name, 
                accepted=accepted
            ).inc()
    
    def record_llm_usage(self, 
                        provider: str, 
                        model: str, 
                        prompt_tokens: int, 
                        completion_tokens: int,
                        cost: float,
                        success: bool):
        """Record LLM usage metrics."""
        
        status = 'success' if success else 'error'
        self.llm_requests_counter.labels(
            provider=provider, 
            model=model, 
            status=status
        ).inc()
        
        self.llm_token_usage.labels(
            provider=provider, 
            model=model, 
            type='prompt'
        ).observe(prompt_tokens)
        
        self.llm_token_usage.labels(
            provider=provider, 
            model=model, 
            type='completion'
        ).observe(completion_tokens)
        
        # Update cost gauge (cumulative)
        current_cost = self.llm_cost_gauge.labels(provider=provider, model=model)._value._value or 0
        self.llm_cost_gauge.labels(provider=provider, model=model).set(current_cost + cost)
    
    def record_convergence_metrics(self, convergence_rate: float, violations: List[str]):
        """Record mathematical convergence metrics."""
        
        self.convergence_rate_gauge.set(convergence_rate)
        
        # Count closure rule violations by type
        for violation_type in violations:
            self.closure_violations_counter.labels(rule_type=violation_type).inc()
    
    def record_system_resources(self, cpu_percent: float, memory_bytes: int, connections: Dict[str, int]):
        """Record system resource usage."""
        
        self.cpu_usage_gauge.labels(component='system').set(cpu_percent)
        self.memory_usage_gauge.labels(component='system', type='total').set(memory_bytes)
        
        for conn_type, count in connections.items():
            self.active_connections_gauge.labels(connection_type=conn_type).set(count)

class MetricsCollector:
    """High-level metrics collection coordinator."""
    
    def __init__(self, quantum_metrics: QuantumMetrics):
        self.quantum_metrics = quantum_metrics
        self.collection_interval = 10.0  # seconds
        self.last_collection_time = 0
    
    def collect_if_due(self, force: bool = False) -> bool:
        """Collect metrics if collection interval has elapsed."""
        current_time = time.time()
        if force or (current_time - self.last_collection_time) >= self.collection_interval:
            self._collect_system_metrics()
            self.last_collection_time = current_time
            return True
        return False
    
    def _collect_system_metrics(self):
        """Collect system-level metrics."""
        # Implementation would gather system resource usage
        # This is a placeholder for actual system metrics collection
        pass
```

**Integration Points**:
- Used by all system components for metrics reporting
- Integrates with Prometheus for metrics scraping
- Connects to Grafana for visualization
- Provides foundation for alerting and anomaly detection

---

### File: `monitoring/tracing.py` (120 LOC)

**Purpose**: OpenTelemetry distributed tracing for tracking quantum state evolution and agent interactions across the system.

**Core Functionality**:
- Distributed trace collection across agent boundaries
- Quantum state context propagation in traces
- Performance bottleneck identification
- Causal relationship tracking between agents
- Custom span attributes for quantum measurements

**Implementation Strategy**: Implements OpenTelemetry standards with quantum-specific span attributes and context propagation ensuring complete visibility into system behavior.

---

### File: `monitoring/logging.py` (100 LOC)

**Purpose**: Structured logging system with quantum context integration and centralized log aggregation.

**Core Functionality**:
- JSON structured logging with quantum state context
- Log level management per component
- Centralized log aggregation and indexing
- Correlation ID tracking for distributed operations
- Performance-optimized async logging

**Implementation Strategy**: High-performance structured logging providing searchable, analyzable logs with quantum state context for debugging and analysis.

---

## 3. Exporters Package (4 Files)

### File: `monitoring/exporters/__init__.py` (5 LOC)

**Purpose**: Exporters package initializer for metrics and telemetry data export.

**Implementation**:
```python
"""
Monitoring Exporters
===================

Export interfaces for sending metrics, traces, and logs to external systems
including Prometheus, Jaeger, and Elasticsearch.
"""

from .prometheus import PrometheusExporter
from .jaeger import JaegerExporter
from .elasticsearch import ElasticsearchExporter

__all__ = ["PrometheusExporter", "JaegerExporter", "ElasticsearchExporter"]
```

---

### File: `monitoring/exporters/prometheus.py` (80 LOC)

**Purpose**: Prometheus metrics exporter with custom collectors and quantum-specific metrics formatting.

**Core Functionality**:
- Custom Prometheus collectors for quantum metrics
- Metric name and label standardization
- High-cardinality metrics optimization
- Push gateway integration for ephemeral jobs
- Quantum state histogram buckets optimization

**Implementation Strategy**: Optimized Prometheus exporter ensuring efficient metrics collection and export while maintaining standard Prometheus formatting.

---

### File: `monitoring/exporters/jaeger.py` (80 LOC)

**Purpose**: Jaeger distributed tracing exporter with quantum context preservation.

**Core Functionality**:
- OpenTelemetry to Jaeger trace export
- Quantum state span attributes preservation
- Trace sampling optimization for performance
- Batch export for high-throughput scenarios
- Custom trace processors for quantum measurements

**Implementation Strategy**: Efficient Jaeger exporter maintaining quantum state context through distributed traces while optimizing for performance.

---

### File: `monitoring/exporters/elasticsearch.py` (80 LOC)

**Purpose**: Elasticsearch log exporter for centralized log aggregation and search.

**Core Functionality**:
- Structured log export to Elasticsearch
- Index template management for log data
- Bulk export optimization for high throughput
- Log retention policy enforcement
- Search-optimized field mapping

**Implementation Strategy**: High-performance Elasticsearch exporter enabling powerful log search and analysis capabilities with automated index management.

---

## 4. Dashboards Package (4 Files)

### File: `monitoring/dashboards/__init__.py` (5 LOC)

**Purpose**: Dashboard configuration package for visualization setup.

**Implementation**: Package initializer for dashboard configurations and templates.

---

### File: `monitoring/dashboards/grafana.json` (500 LOC)

**Purpose**: Comprehensive Grafana dashboard configuration for QuantaCirc system monitoring.

**Core Functionality**:
- Quantum state evolution visualization
- Agent performance dashboards
- System health monitoring panels
- Mathematical convergence tracking
- Real-time alerting integration

**Implementation Strategy**: Complete Grafana dashboard providing comprehensive system visibility through carefully designed panels and visualizations for quantum-mechanical software engineering metrics.

---

### File: `monitoring/dashboards/prometheus.yml` (50 LOC)

**Purpose**: Prometheus configuration for scraping QuantaCirc metrics.

**Core Functionality**:
- Scrape target configuration for all components
- Recording rules for derived metrics
- Alerting rules for critical conditions
- Retention policy configuration
- Federation setup for multi-cluster monitoring

**Implementation Strategy**: Optimized Prometheus configuration ensuring reliable metrics collection with appropriate retention and alerting.

---

### File: `monitoring/dashboards/jaeger.yml` (40 LOC)

**Purpose**: Jaeger configuration for distributed tracing collection.

**Core Functionality**:
- Trace collection and storage configuration
- Sampling strategy optimization
- UI configuration for quantum trace analysis
- Storage backend configuration
- Performance tuning parameters

**Implementation Strategy**: Efficient Jaeger configuration optimized for quantum system tracing requirements.

---

## 5. Health Monitoring Package (4 Files)

### File: `monitoring/health/__init__.py` (5 LOC)

**Purpose**: Health monitoring package initializer.

**Implementation**: Package initializer exposing health check interfaces and utilities.

---

### File: `monitoring/health/readiness.py` (60 LOC)

**Purpose**: Kubernetes readiness probe implementation checking system readiness to accept traffic.

**Core Functionality**:
- Quantum state consistency verification
- Database connectivity checking
- Message bus availability validation
- Agent system readiness assessment
- External dependency health verification

**Implementation Strategy**: Comprehensive readiness checking ensuring system is fully operational before accepting requests.

---

### File: `monitoring/health/liveness.py` (60 LOC)

**Purpose**: Kubernetes liveness probe implementation for detecting system health problems.

**Core Functionality**:
- Core system process health monitoring
- Deadlock and hang detection
- Resource exhaustion checking
- Critical error threshold monitoring
- Automatic restart trigger conditions

**Implementation Strategy**: Robust liveness monitoring preventing zombie processes and ensuring system reliability.

---

### File: `monitoring/health/dependency.py` (80 LOC)

**Purpose**: External dependency health monitoring for third-party services.

**Core Functionality**:
- LLM provider availability checking
- Database connection health monitoring
- Message broker connectivity verification
- External API endpoint validation
- Dependency circuit breaker integration

**Implementation Strategy**: Proactive dependency monitoring enabling graceful degradation and failover capabilities.

---

## 6. Advanced Monitoring Components (2 Files)

### File: `monitoring/anomaly_detector.py` (150 LOC)

**Purpose**: Machine learning-based anomaly detection for quantum system behavior monitoring.

**Core Functionality**:
- Quantum state anomaly detection using statistical methods
- Agent behavior pattern analysis
- Performance regression detection
- Automated alert generation for anomalies
- Historical baseline learning and adaptation

**Implementation Strategy**:
```python
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

from core.types import QCState, AgentResult

@dataclass
class AnomalyAlert:
    """Represents an detected anomaly."""
    timestamp: datetime
    component: str
    anomaly_type: str
    severity: str  # low, medium, high, critical
    description: str
    metric_values: Dict[str, float]
    confidence_score: float
    recommended_actions: List[str]

class QuantumAnomalyDetector:
    """
    Machine learning-based anomaly detector for quantum system monitoring.
    
    Uses statistical methods and machine learning models to detect unusual
    behavior in quantum state evolution, agent performance, and system metrics.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize models for different types of anomalies
        self.quantum_state_detector = IsolationForest(
            contamination=0.1,  # Expected anomaly rate
            random_state=42
        )
        self.agent_performance_detector = IsolationForest(
            contamination=0.05,
            random_state=42
        )
        
        # Scalers for feature normalization
        self.quantum_scaler = StandardScaler()
        self.agent_scaler = StandardScaler()
        
        # Historical data for baseline learning
        self.quantum_state_history: List[np.ndarray] = []
        self.agent_performance_history: List[np.ndarray] = []
        
        # Training status
        self.quantum_model_trained = False
        self.agent_model_trained = False
        
        # Anomaly detection thresholds
        self.quantum_threshold = -0.5
        self.agent_threshold = -0.4
        
        # Minimum samples required for training
        self.min_training_samples = 100
    
    def process_quantum_state(self, state: QCState) -> Optional[AnomalyAlert]:
        """
        Process quantum state and detect anomalies.
        
        Args:
            state: Current quantum state
            
        Returns:
            AnomalyAlert if anomaly detected, None otherwise
        """
        # Extract features from quantum state
        features = self._extract_quantum_features(state)
        
        # Add to history for baseline learning
        self.quantum_state_history.append(features)
        
        # Keep only recent history (sliding window)
        max_history = self.config.get('max_history_size', 10000)
        if len(self.quantum_state_history) > max_history:
            self.quantum_state_history = self.quantum_state_history[-max_history:]
        
        # Train model if we have enough samples
        if (not self.quantum_model_trained and 
            len(self.quantum_state_history) >= self.min_training_samples):
            self._train_quantum_model()
        
        # Detect anomalies if model is trained
        if self.quantum_model_trained:
            return self._detect_quantum_anomaly(state, features)
        
        return None
    
    def process_agent_result(self, agent_name: str, result: AgentResult, duration: float) -> Optional[AnomalyAlert]:
        """
        Process agent execution result and detect performance anomalies.
        
        Args:
            agent_name: Name of the agent
            result: Agent execution result
            duration: Execution duration
            
        Returns:
            AnomalyAlert if anomaly detected, None otherwise
        """
        # Extract performance features
        features = self._extract_agent_features(result, duration)
        
        # Add to history
        self.agent_performance_history.append(features)
        
        # Keep sliding window of history
        max_history = self.config.get('max_history_size', 10000)
        if len(self.agent_performance_history) > max_history:
            self.agent_performance_history = self.agent_performance_history[-max_history:]
        
        # Train model if needed
        if (not self.agent_model_trained and 
            len(self.agent_performance_history) >= self.min_training_samples):
            self._train_agent_model()
        
        # Detect anomalies
        if self.agent_model_trained:
            return self._detect_agent_anomaly(agent_name, result, features, duration)
        
        return None
    
    def _extract_quantum_features(self, state: QCState) -> np.ndarray:
        """Extract numerical features from quantum state for anomaly detection."""
        features = []
        
        # Core quantum measurements
        features.append(state.energy)
        
        if hasattr(state, 'lyapunov_potential'):
            features.append(state.lyapunov_potential)
        else:
            features.append(0.0)
        
        if hasattr(state, 'contraction_factor'):
            features.append(state.contraction_factor)
        else:
            features.append(1.0)
        
        # Energy components if available
        if hasattr(state, 'energy_components'):
            components = state.energy_components
            features.extend([components.static, components.dynamic, components.interaction])
        else:
            features.extend([0.0, 0.0, 0.0])
        
        # Phase encoding (numerical)
        phase_encoding = 1.0 if hasattr(state, 'optimization_phase') and state.optimization_phase == 'exploration' else 0.0
        features.append(phase_encoding)
        
        # Time-based features
        if hasattr(state, 'timestamp'):
            # Hour of day (cyclical encoding)
            hour = state.timestamp.hour
            features.extend([np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24)])
        else:
            features.extend([0.0, 0.0])
        
        return np.array(features)
    
    def _extract_agent_features(self, result: AgentResult, duration: float) -> np.ndarray:
        """Extract numerical features from agent execution for anomaly detection."""
        features = []
        
        # Execution metrics
        features.append(duration)
        features.append(1.0 if result.action_taken else 0.0)
        features.append(1.0 if result.error else 0.0)
        
        # Energy impact if available
        if hasattr(result, 'energy_delta') and result.energy_delta:
            total_delta = sum(result.energy_delta.values())
            features.append(total_delta)
            features.append(abs(total_delta))  # Magnitude of change
        else:
            features.extend([0.0, 0.0])
        
        # Memory and CPU usage (if available)
        if hasattr(result, 'resource_usage'):
            usage = result.resource_usage
            features.append(usage.get('memory_mb', 0))
            features.append(usage.get('cpu_percent', 0))
        else:
            features.extend([0.0, 0.0])
        
        return np.array(features)
    
    def _train_quantum_model(self):
        """Train the quantum state anomaly detection model."""
        try:
            # Convert history to training data
            training_data = np.array(self.quantum_state_history)
            
            # Normalize features
            normalized_data = self.quantum_scaler.fit_transform(training_data)
            
            # Train isolation forest
            self.quantum_state_detector.fit(normalized_data)
            self.quantum_model_trained = True
            
            self.logger.info(f"Trained quantum anomaly model with {len(training_data)} samples")
            
        except Exception as e:
            self.logger.error(f"Failed to train quantum anomaly model: {e}")
    
    def _train_agent_model(self):
        """Train the agent performance anomaly detection model."""
        try:
            # Convert history to training data
            training_data = np.array(self.agent_performance_history)
            
            # Normalize features
            normalized_data = self.agent_scaler.fit_transform(training_data)
            
            # Train isolation forest
            self.agent_performance_detector.fit(normalized_data)
            self.agent_model_trained = True
            
            self.logger.info(f"Trained agent anomaly model with {len(training_data)} samples")
            
        except Exception as e:
            self.logger.error(f"Failed to train agent anomaly model: {e}")
    
    def _detect_quantum_anomaly(self, state: QCState, features: np.ndarray) -> Optional[AnomalyAlert]:
        """Detect quantum state anomalies using trained model."""
        try:
            # Normalize features
            normalized_features = self.quantum_scaler.transform([features])
            
            # Get anomaly score
            anomaly_score = self.quantum_state_detector.decision_function(normalized_features)[0]
            
            if anomaly_score < self.quantum_threshold:
                # Determine severity based on score
                if anomaly_score < -0.8:
                    severity = "critical"
                elif anomaly_score < -0.7:
                    severity = "high"
                elif anomaly_score
