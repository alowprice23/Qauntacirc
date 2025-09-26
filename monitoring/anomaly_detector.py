import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

# from core.types import QCState, AgentResult # This will be uncommented later

# Placeholder for core.types
class QCState:
    energy: float = 0.0
    energy_components: dict = field(default_factory=dict)
    lyapunov_potential: float = 0.0
    contraction_factor: float = 0.0
    optimization_phase: str = "A"
    timestamp: Any = None

class AgentResult:
    action_taken: bool = False
    error: bool = False
    energy_delta: dict = field(default_factory=dict)
    proposal_generated: bool = False
    resource_usage: dict = field(default_factory=dict)


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
        if hasattr(state, 'energy_components') and state.energy_components:
            components = state.energy_components
            features.extend([components.get('static', 0), components.get('dynamic', 0), components.get('interaction', 0)])
        else:
            features.extend([0.0, 0.0, 0.0])

        # Phase encoding (numerical)
        phase_encoding = 1.0 if hasattr(state, 'optimization_phase') and state.optimization_phase == 'exploration' else 0.0
        features.append(phase_encoding)

        # Time-based features
        if hasattr(state, 'timestamp') and state.timestamp:
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
        if hasattr(result, 'resource_usage') and result.resource_usage:
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
                else:
                    severity = "medium"

                return AnomalyAlert(
                    timestamp=datetime.now(),
                    component="QuantumState",
                    anomaly_type="UnexpectedState",
                    severity=severity,
                    description=f"Unusual quantum state detected with score {anomaly_score:.2f}",
                    metric_values={"energy": state.energy, "lyapunov": state.lyapunov_potential},
                    confidence_score=1 - anomaly_score,
                    recommended_actions=["Investigate system state", "Review recent agent actions"]
                )
        except Exception as e:
            self.logger.error(f"Error during quantum anomaly detection: {e}")

        return None

    def _detect_agent_anomaly(self, agent_name: str, result: AgentResult, features: np.ndarray, duration: float) -> Optional[AnomalyAlert]:
        """Detect agent performance anomalies using trained model."""
        try:
            # Normalize features
            normalized_features = self.agent_scaler.transform([features])

            # Get anomaly score
            anomaly_score = self.agent_performance_detector.decision_function(normalized_features)[0]

            if anomaly_score < self.agent_threshold:
                severity = "high" if anomaly_score < -0.6 else "medium"

                return AnomalyAlert(
                    timestamp=datetime.now(),
                    component=f"Agent({agent_name})",
                    anomaly_type="PerformanceAnomaly",
                    severity=severity,
                    description=f"Unusual agent behavior detected with score {anomaly_score:.2f}",
                    metric_values={"duration": duration, "error": 1.0 if result.error else 0.0},
                    confidence_score=1 - anomaly_score,
                    recommended_actions=["Check agent logs", "Analyze agent performance trends"]
                )
        except Exception as e:
            self.logger.error(f"Error during agent anomaly detection: {e}")

        return None