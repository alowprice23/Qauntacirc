# monitoring/anomaly_detector.py

import numpy as np
from sklearn.ensemble import IsolationForest
from collections import deque
import logging
import json

# Configure a basic logger for alerts
logging.basicConfig(level=logging.INFO)
alert_logger = logging.getLogger("AnomalyAlerts")

class QuantumAnomalyDetector:
    """
    Detects anomalies in quantum system states and agent behavior using an
    Isolation Forest machine learning model. This detector can be trained on
    normal operational data and then used to identify outliers in real-time.
    """

    def __init__(self, contamination=0.01, n_estimators=100, random_state=42, history_size=1000):
        """
        Initializes the anomaly detector.
        Args:
            contamination (float): The expected proportion of anomalies in the
                                   dataset. This is a key parameter for the
                                   Isolation Forest model.
            n_estimators (int): The number of base estimators (trees) in the
                                ensemble.
            random_state (int): Seed for the random number generator for
                                reproducibility.
            history_size (int): The number of recent data points to keep for
                                contextual analysis.
        """
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
            bootstrap=True
        )
        self.is_trained = False
        self.history = deque(maxlen=history_size)

    def train(self, normal_data: np.ndarray):
        """
        Trains the anomaly detection model on a dataset of normal behavior.
        The model learns the patterns of normal data to be able to distinguish
        outliers.
        Args:
            normal_data (np.ndarray): A 2D array where each row is a data
                                      point and each column is a feature
                                      (e.g., energy, lyapunov exponent).
        """
        if normal_data.ndim != 2 or normal_data.shape[0] < 10:
            raise ValueError("`normal_data` must be a 2D array with at least 10 samples.")
        self.model.fit(normal_data)
        self.is_trained = True
        alert_logger.info("Anomaly detection model trained successfully.")

    def predict(self, data_point: np.ndarray) -> int:
        """
        Predicts whether a single data point is an anomaly.
        Args:
            data_point (np.ndarray): A 1D array representing a single data point
                                     with the same features used for training.
        Returns:
            int: -1 for an anomaly, 1 for a normal data point.
        """
        if not self.is_trained:
            raise RuntimeError("The anomaly detection model has not been trained yet.")

        prediction = self.model.predict(data_point.reshape(1, -1))
        self.history.append(data_point)

        if prediction[0] == -1:
            self.trigger_alert(
                "Quantum State Anomaly",
                {"reason": "Isolation forest outlier detection", "data_point": data_point.tolist()}
            )

        return int(prediction[0])

    def detect_performance_regression(self, agent_execution_times: list, threshold_std: float = 3.0) -> bool:
        """
        Detects performance regressions in agent execution times using a
        statistical approach (3-sigma rule).
        Args:
            agent_execution_times (list): A list of recent execution times for an agent.
            threshold_std (float): The number of standard deviations from the
                                   mean to consider as a regression.
        Returns:
            bool: True if a regression is detected, False otherwise.
        """
        if len(agent_execution_times) < 20:
            return False  # Not enough data for a reliable statistical measure

        moving_avg = np.mean(agent_execution_times)
        moving_std = np.std(agent_execution_times)
        latest_metric = agent_execution_times[-1]

        if latest_metric > moving_avg + (moving_std * threshold_std):
            self.trigger_alert(
                "Agent Performance Regression",
                {
                    "reason": "Execution time exceeded statistical threshold",
                    "latest_time": latest_metric,
                    "moving_average": moving_avg,
                    "std_dev": moving_std,
                }
            )
            return True
        return False

    def trigger_alert(self, alert_type: str, details: dict):
        """
        Triggers an alert. In a real system, this would integrate with an
        alerting service like PagerDuty, Opsgenie, or send a notification
        to a Slack channel.
        Args:
            alert_type (str): The type of alert (e.g., "Quantum State Anomaly").
            details (dict): A dictionary containing the details of the anomaly.
        """
        alert_message = json.dumps({"alert_type": alert_type, "details": details})
        alert_logger.warning(alert_message)
