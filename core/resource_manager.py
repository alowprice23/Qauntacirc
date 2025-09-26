import psutil
from typing import Optional

class ResourceManager:
    def __init__(self, cpu_limit: Optional[float] = None, memory_limit: Optional[float] = None):
        """
        Initializes the ResourceManager with optional resource limits.

        Args:
            cpu_limit (float, optional): CPU usage limit in percent (e.g., 80.0).
            memory_limit (float, optional): Memory usage limit in percent (e.g., 80.0).
        """
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit

    def is_within_limits(self) -> bool:
        """
        Checks if the current resource usage is within the defined limits.

        Returns:
            bool: True if usage is within limits or if limits are not set, False otherwise.
        """
        if self.cpu_limit is not None:
            current_cpu = psutil.cpu_percent(interval=1)
            if current_cpu > self.cpu_limit:
                print(f"Throttling due to high CPU usage: {current_cpu}% > {self.cpu_limit}%")
                return False

        if self.memory_limit is not None:
            current_memory = psutil.virtual_memory().percent
            if current_memory > self.memory_limit:
                print(f"Throttling due to high memory usage: {current_memory}% > {self.memory_limit}%")
                return False

        return True

    def get_current_usage(self) -> dict:
        """
        Returns the current CPU and memory usage.
        """
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_percent": psutil.virtual_memory().percent,
        }