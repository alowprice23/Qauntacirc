# monitoring/exporters/prometheus.py

from prometheus_client import start_http_server, push_to_gateway, REGISTRY
import threading
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PrometheusExporter:
    """
    Manages the exposure of metrics to Prometheus. This class can start a
    long-running HTTP server for standard Prometheus scraping or push metrics
    to a Pushgateway for short-lived jobs.
    """

    def __init__(self, port: int = 8000, pushgateway_url: Optional[str] = None):
        """
        Initializes the Prometheus exporter.
        Args:
            port (int): The port on which to expose the metrics via an HTTP server.
            pushgateway_url (str, optional): The URL of a Prometheus Pushgateway.
                                             If provided, enables pushing metrics.
                                             Defaults to None.
        """
        self.port = port
        self.pushgateway_url = pushgateway_url
        self._server_thread = None

    def start_server(self):
        """
        Starts the Prometheus metrics server in a daemon thread. This is the
        standard way to expose metrics for services that are continuously running.
        """
        if self._server_thread is not None and self._server_thread.is_alive():
            logger.warning("Prometheus server is already running.")
            return

        try:
            self._server_thread = threading.Thread(
                target=start_http_server, args=(self.port, REGISTRY)
            )
            self._server_thread.daemon = True
            self._server_thread.start()
            logger.info(f"Prometheus exporter server started on port {self.port}.")
        except Exception as e:
            logger.error(f"Failed to start Prometheus server: {e}")
            raise

    def push_metrics(self, job_name: str, instance_name: str):
        """
        Pushes the current state of all metrics in the registry to the configured
        Prometheus Pushgateway. This is useful for batch jobs or serverless
        functions that are not long-running enough to be scraped.
        Args:
            job_name (str): The name of the job to associate with the metrics.
            instance_name (str): A unique identifier for the instance of the job.
        """
        if not self.pushgateway_url:
            raise ValueError("Pushgateway URL is not configured. Cannot push metrics.")

        try:
            push_to_gateway(
                self.pushgateway_url,
                job=job_name,
                registry=REGISTRY,
                grouping_key={"instance": instance_name},
            )
            logger.info(f"Successfully pushed metrics to {self.pushgateway_url} for job '{job_name}'.")
        except Exception as e:
            logger.error(f"Failed to push metrics to Pushgateway: {e}")
            raise

    def optimize_collectors(self):
        """
        A placeholder for logic to optimize metrics collection, particularly for
        high-cardinality metrics. In a real-world scenario, this could involve
        implementing custom collectors that pre-aggregate data, or removing
        metrics with unbounded label values.
        """
        logger.info("Running high-cardinality metric optimization (simulation)...")
        # Example: Unregister a metric to reduce cardinality.
        # from monitoring.metrics import SOME_HIGH_CARDINALITY_METRIC
        # REGISTRY.unregister(SOME_HIGH_CARDINALITY_METRIC)
        pass
