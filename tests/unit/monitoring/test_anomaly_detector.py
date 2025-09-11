# tests/unit/monitoring/test_anomaly_detector.py

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from monitoring.anomaly_detector import QuantumAnomalyDetector

@pytest.fixture
def detector():
    """Fixture for a QuantumAnomalyDetector instance."""
    return QuantumAnomalyDetector(history_size=100, contamination=0.01)

def test_initialization(detector):
    """Test that the detector initializes with the correct parameters."""
    assert detector.model.contamination == 0.01
    assert not detector.is_trained
    assert detector.history.maxlen == 100

def test_train_model(detector):
    """Test the training of the Isolation Forest model."""
    # Generate some normal-looking data
    normal_data = np.random.randn(100, 2) * 0.5

    detector.train(normal_data)
    assert detector.is_trained

def test_train_model_invalid_data(detector):
    """Test that training fails with invalid data shapes."""
    with pytest.raises(ValueError):
        detector.train(np.random.randn(5, 2)) # Not enough samples
    with pytest.raises(ValueError):
        detector.train(np.random.randn(20)) # Must be 2D array

@patch('monitoring.anomaly_detector.alert_logger')
def test_predict_anomaly(mock_logger, detector):
    """Test the prediction of an anomalous data point."""
    normal_data = np.random.randn(100, 2)
    detector.train(normal_data)

    # Anomaly is a point far from the trained data
    anomaly_point = np.array([[10, 10]])
    prediction = detector.predict(anomaly_point)

    assert prediction == -1 # -1 indicates an anomaly
    assert len(detector.history) == 1
    assert np.array_equal(detector.history[0], anomaly_point)

    # Check that an alert was triggered
    mock_logger.warning.assert_called_once()
    call_args = mock_logger.warning.call_args[0][0]
    assert '"alert_type": "Quantum State Anomaly"' in call_args

def test_predict_normal(detector):
    """Test the prediction of a normal data point."""
    normal_data = np.zeros((100, 2))
    detector.train(normal_data)

    normal_point = np.array([0.1, -0.1])
    prediction = detector.predict(normal_point)

    assert prediction == 1 # 1 indicates a normal point
    assert len(detector.history) == 1

def test_predict_untrained_model(detector):
    """Test that prediction fails if the model is not trained."""
    with pytest.raises(RuntimeError):
        detector.predict(np.array([1, 1]))

@patch('monitoring.anomaly_detector.alert_logger')
def test_performance_regression_detected(mock_logger, detector):
    """Test detection of a performance regression."""
    # Baseline times
    times = list(np.random.normal(loc=1.0, scale=0.1, size=50))
    # Add a spike
    times.append(5.0)

    regression_detected = detector.detect_performance_regression(times, threshold_std=3.0)

    assert regression_detected
    mock_logger.warning.assert_called_once()
    call_args = mock_logger.warning.call_args[0][0]
    assert '"alert_type": "Agent Performance Regression"' in call_args

def test_performance_regression_not_detected(detector):
    """Test that normal performance does not trigger a regression alert."""
    times = list(np.random.normal(loc=1.0, scale=0.1, size=50))

    regression_detected = detector.detect_performance_regression(times, threshold_std=3.0)
    assert not regression_detected

def test_performance_regression_insufficient_data(detector):
    """Test that no regression is detected with insufficient data."""
    times = [1.0, 1.1, 5.0] # Not enough data points
    regression_detected = detector.detect_performance_regression(times)
    assert not regression_detected
