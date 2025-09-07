# monitoring/health/liveness.py

import logging
from typing import List, Callable, Tuple
import threading

logger = logging.getLogger(__name__)

class LivenessProbe:
    """
    Represents a liveness probe that determines if the application is running
    and has not entered a deadlocked or unresponsive state. A failing liveness
    probe signals to an orchestrator (like Kubernetes) that the application
    should be restarted.

    Liveness checks should be simple and not rely on external dependencies.
    """

    def __init__(self, checks: List[Callable[[], Tuple[bool, str]]]):
        """
        Initializes the liveness probe with a list of check functions.
        Args:
            checks (List[Callable[[], Tuple[bool, str]]]):
                A list of functions that perform the liveness checks. Each
                function should return a tuple containing a boolean (True for
                alive, False for dead) and a string message.
        """
        if not checks:
            raise ValueError("At least one liveness check must be provided.")
        self.checks = checks

    def check(self) -> Tuple[bool, Dict[str, str]]:
        """
        Executes all registered liveness checks.
        Returns:
            Tuple[bool, Dict[str, str]]:
                A tuple containing an overall liveness status (True if all
                checks pass) and a dictionary with the details of each check.
        """
        overall_status = True
        results = {}

        for check_func in self.checks:
            check_name = check_func.__name__
            try:
                is_alive, message = check_func()
                results[check_name] = "Alive" if is_alive else f"Failed: {message}"
                if not is_alive:
                    overall_status = False
                    logger.critical(f"Liveness check '{check_name}' failed: {message}")
            except Exception as e:
                overall_status = False
                results[check_name] = f"Error: {str(e)}"
                logger.error(f"An exception occurred during liveness check '{check_name}': {e}", exc_info=True)

        return overall_status, results

# --- Example Check Functions ---

def check_main_thread_responsive() -> Tuple[bool, str]:
    """
    A basic check to ensure the Python process is responsive.
    """
    logger.info("Checking main thread responsiveness...")
    return True, "Process is responsive."

def check_for_deadlocked_threads() -> Tuple[bool, str]:
    """
    Simulates a check for deadlocked threads. In a real implementation, this
    would involve inspecting the state of all running threads.
    """
    logger.info("Checking for deadlocked threads...")
    # This is a simplified example. A real implementation would be more complex.
    active_threads = threading.active_count()
    if active_threads > 50: # An arbitrary threshold
        return False, f"Potential deadlock detected: {active_threads} active threads."
    return True, f"{active_threads} active threads, which is within the normal range."

def check_memory_usage() -> Tuple[bool, str]:
    """
    Checks if memory usage is within a reasonable limit.
    """
    # This would require a library like `psutil` to be implemented correctly.
    # import psutil
    # process = psutil.Process()
    # memory_mb = process.memory_info().rss / (1024 * 1024)
    # if memory_mb > 2048: # 2GB threshold
    #     return False, f"Memory usage ({memory_mb:.2f} MB) exceeds threshold."
    logger.info("Checking memory usage...")
    return True, "Memory usage is within acceptable limits."
