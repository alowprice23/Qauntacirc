# monitoring/health/readiness.py

import logging
from typing import List, Callable, Tuple

logger = logging.getLogger(__name__)

class ReadinessProbe:
    """
    Represents a readiness probe that determines if the application is ready to
    accept traffic. Readiness can depend on various factors, such as the
    availability of downstream services, database connections, or the completion
    of initialization tasks.
    """

    def __init__(self, checks: List[Callable[[], Tuple[bool, str]]]):
        """
        Initializes the readiness probe with a list of check functions.
        Args:
            checks (List[Callable[[], Tuple[bool, str]]]):
                A list of functions that perform the readiness checks. Each
                function should return a tuple containing a boolean (True for
                success, False for failure) and a string message describing
                the result.
        """
        if not checks:
            raise ValueError("At least one readiness check must be provided.")
        self.checks = checks

    def check(self) -> Tuple[bool, Dict[str, str]]:
        """
        Executes all registered readiness checks and aggregates the results.
        Returns:
            Tuple[bool, Dict[str, str]]:
                A tuple containing an overall readiness status (True if all
                checks pass, False otherwise) and a dictionary with the
                details of each check.
        """
        overall_status = True
        results = {}

        for check_func in self.checks:
            check_name = check_func.__name__
            try:
                is_ready, message = check_func()
                results[check_name] = "Ready" if is_ready else f"Not Ready: {message}"
                if not is_ready:
                    overall_status = False
                    logger.warning(f"Readiness check '{check_name}' failed: {message}")
            except Exception as e:
                overall_status = False
                results[check_name] = f"Error: {str(e)}"
                logger.error(f"An exception occurred during readiness check '{check_name}': {e}", exc_info=True)

        if overall_status:
            logger.info("All readiness checks passed successfully.")

        return overall_status, results

# --- Example Check Functions ---

def check_database_connection() -> Tuple[bool, str]:
    """Simulates a check for a database connection."""
    # In a real application, this would involve trying to connect to the DB.
    logger.info("Checking database connection...")
    return True, "Database connection is active."

def check_quantum_subsystem_initialized() -> Tuple[bool, str]:
    """Simulates a check for the initialization of a critical subsystem."""
    logger.info("Checking quantum subsystem...")
    # Replace with actual initialization logic
    is_initialized = True
    if is_initialized:
        return True, "Quantum subsystem is online."
    else:
        return False, "Quantum subsystem is still initializing."

def check_downstream_service() -> Tuple[bool, str]:
    """Simulates a check for a downstream service dependency."""
    logger.info("Pinging downstream service...")
    # In a real application, this would make an HTTP request or similar.
    is_available = True
    if is_available:
        return True, "Downstream service is responsive."
    else:
        return False, "Downstream service is not available."
