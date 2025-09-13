import re
from typing import List, Dict

class CommandDecomposer:
    """
    Decomposes a complex natural language command into atomic operations.
    This is a simplified implementation using keyword matching.
    """

    def __init__(self, keywords: List[str] = None):
        if keywords is None:
            # These keywords represent potential atomic operations.
            self.keywords = [
                "build microservices", "build", "auth", "rate limiting",
                "monitoring", "deployment automation", "deploy",
                "generate comprehensive tests", "test", "optimize for 10k RPS", "optimize"
            ]
        else:
            self.keywords = keywords

    def decompose(self, command: str) -> Dict[str, List[str]]:
        """
        Decomposes the command into a list of atomic operations.

        Args:
            command: The complex command string.

        Returns:
            A dictionary containing the list of identified operations.
        """
        # Normalize the command to lowercase for easier matching
        normalized_command = command.lower()

        atomic_operations = []
        # Use regex to find all occurrences of keywords
        # The keywords are sorted by length to match longer phrases first
        sorted_keywords = sorted(self.keywords, key=len, reverse=True)

        # A simple way to find operations in the command
        # This is a placeholder for a more sophisticated NLP model
        for keyword in sorted_keywords:
            if keyword in normalized_command:
                atomic_operations.append(keyword)
                # Remove the found keyword to avoid re-matching parts of it
                normalized_command = normalized_command.replace(keyword, "", 1)

        # A more robust approach would use NLP to understand the sentence structure,
        # but for this simulation, keyword matching is a good start.

        return {"atomic_operations": atomic_operations}
