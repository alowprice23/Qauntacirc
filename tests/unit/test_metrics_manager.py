import unittest
import time
from core.metrics_manager import MetricsManager

class TestMetricsManager(unittest.TestCase):
    def setUp(self):
        self.metrics_manager = MetricsManager()

    def test_increment_counter(self):
        self.metrics_manager.increment_counter("test_counter")
        self.assertEqual(self.metrics_manager.counters["test_counter"], 1)
        self.metrics_manager.increment_counter("test_counter", value=5)
        self.assertEqual(self.metrics_manager.counters["test_counter"], 6)

    def test_observe_histogram(self):
        self.metrics_manager.observe_histogram("test_histogram", 10.5)
        self.metrics_manager.observe_histogram("test_histogram", 20.0)
        self.assertEqual(self.metrics_manager.histograms["test_histogram"], [10.5, 20.0])

    def test_set_gauge(self):
        self.metrics_manager.set_gauge("test_gauge", 42.0)
        self.assertEqual(self.metrics_manager.gauges["test_gauge"], 42.0)
        self.metrics_manager.set_gauge("test_gauge", -10.5)
        self.assertEqual(self.metrics_manager.gauges["test_gauge"], -10.5)

    def test_get_metrics(self):
        self.metrics_manager.increment_counter("counter1")
        self.metrics_manager.observe_histogram("hist1", 10)
        self.metrics_manager.observe_histogram("hist1", 20)
        self.metrics_manager.set_gauge("gauge1", 123.45)

        metrics = self.metrics_manager.get_metrics()

        expected_metrics = {
            "counters": {"counter1": 1},
            "histograms": {"hist1": {"sum": 30, "count": 2}},
            "gauges": {"gauge1": 123.45},
        }
        self.assertEqual(metrics, expected_metrics)

    def test_track_execution_time(self):
        # The context manager needs to be created from the manager instance
        context_manager = self.metrics_manager.track_execution_time("my_timed_block")

        with context_manager:
            time.sleep(0.01) # Simulate some work

        self.assertIn("my_timed_block_duration_seconds", self.metrics_manager.histograms)
        self.assertEqual(len(self.metrics_manager.histograms["my_timed_block_duration_seconds"]), 1)
        duration = self.metrics_manager.histograms["my_timed_block_duration_seconds"][0]
        self.assertGreater(duration, 0.0)
        self.assertLess(duration, 0.1)

if __name__ == '__main__':
    unittest.main()