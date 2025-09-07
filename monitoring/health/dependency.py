# monitoring/health/dependency.py

import logging
import requests
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class DependencyChecker:
    """
    Provides a mechanism to check the health and availability of external
    dependencies, such as downstream services, databases, or message brokers.
    These checks are typically exposed via a dedicated health endpoint for
    diagnostic purposes.
    """

    def __init__(self, dependencies: List[Dict[str, Any]]):
        """
        Initializes the dependency checker.
        Args:
            dependencies (List[Dict[str, Any]]):
                A list of dictionaries, where each dictionary defines a
                dependency to be checked. The dictionary should include a 'name',
                'type' (e.g., 'http'), and other necessary details like 'url'.
        """
        self.dependencies = dependencies

    def check_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Checks the health of all configured dependencies and returns a detailed report.
        Returns:
            Dict[str, Dict[str, Any]]:
                A dictionary where keys are dependency names and values are
                dictionaries containing the status ('healthy' or 'unhealthy')
                and additional details.
        """
        results = {}
        for dep in self.dependencies:
            name = dep.get("name", "unnamed_dependency")
            dep_type = dep.get("type")

            try:
                if dep_type == "http":
                    status, details = self._check_http_dependency(dep.get("url"), dep.get("timeout", 5))
                elif dep_type == "database":
                    # Placeholder for a database check
                    status, details = self._check_database_dependency(dep)
                else:
                    status, details = "unknown", f"Unsupported dependency type: {dep_type}"

                results[name] = {"status": status, "details": details}

            except Exception as e:
                logger.error(f"Failed to check dependency '{name}': {e}", exc_info=True)
                results[name] = {"status": "unhealthy", "details": str(e)}

        return results

    def _check_http_dependency(self, url: str, timeout: int) -> Tuple[str, str]:
        """
        Checks an HTTP-based dependency by making a GET request to its health endpoint.
        """
        if not url:
            return "unhealthy", "URL is not configured."

        logger.info(f"Checking HTTP dependency at {url}...")
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raises an exception for 4xx or 5xx status codes
        return "healthy", f"Received status code {response.status_code}."

    def _check_database_dependency(self, db_config: Dict[str, Any]) -> Tuple[str, str]:
        """
        Placeholder for a database dependency check. In a real implementation,
        this would attempt to establish a connection and run a simple query.
        """
        logger.info(f"Checking database dependency '{db_config.get('name')}'...")
        # Example:
        # import psycopg2
        # conn = psycopg2.connect(**db_config.get('connection_params'))
        # conn.close()
        return "healthy", "Database connection successful (simulated)."
