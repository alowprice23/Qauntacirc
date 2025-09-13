from typing import List, Dict, Any

class CommandHistory:
    """
    Stores and retrieves historical command data.
    This serves as a simple, in-memory "ConstellationMemory".
    """
    def __init__(self):
        self._history: List[Dict[str, Any]] = []

    def add_entry(self, command_details: Dict[str, Any]):
        """
        Adds a new command execution record to the history.
        """
        self._history.append(command_details)

    def query_history(self, query_text: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Queries the history for commands that are similar to the query text.
        The filtering is a simplified version of the "ConstellationQuery".
        """
        # A simple search: find commands that start with the query text.
        # A real implementation would use more advanced text similarity (e.g., embeddings).
        matches = [
            record for record in self._history
            if record.get("command", "").lower().startswith(query_text.lower())
        ]

        if filters:
            if "min_complexity" in filters:
                matches = [m for m in matches if m.get("mathematical_complexity", 0) >= filters["min_complexity"]]
            if "max_energy_impact" in filters:
                matches = [m for m in matches if m.get("energy_impact_prediction", 0) <= filters["max_energy_impact"]]

        return matches

    def get_all_history(self) -> List[Dict[str, Any]]:
        """Returns the entire command history."""
        return self._history
