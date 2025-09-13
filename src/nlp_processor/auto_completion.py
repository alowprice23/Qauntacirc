from typing import List, Dict, Any
from .command_history import CommandHistory
from collections import Counter

class AutoCompletion:
    """
    Provides intelligent auto-completion suggestions for partial commands.
    This is the practical implementation of "PhysicsBasedAutoCompletion".
    """
    def __init__(self, history: CommandHistory):
        self.history = history

    def get_suggestions(self, partial_input: str) -> Dict[str, Any]:
        """
        Generates and ranks completion suggestions based on command history.
        """
        if not partial_input:
            return {"suggestions": []}

        # 1. Query history for commands matching the partial input.
        matching_records = self.history.query_history(partial_input)

        if not matching_records:
            return {"suggestions": []}

        # 2. Score and rank the suggestions.
        # We'll use frequency and "energy efficiency" for the score.
        command_counts = Counter(record["command"] for record in matching_records)

        suggestions = []
        # Use a set to avoid adding the same command suggestion multiple times
        processed_commands = set()

        for record in matching_records:
            command = record["command"]
            if command in processed_commands:
                continue

            freq = command_counts[command]
            energy = record.get("energy_impact_prediction", 1)

            # The "physics_score" is a heuristic.
            # Higher frequency is better. Lower energy is better.
            # Formula: score = frequency / log(energy + 1.1) to avoid log(1)=0
            import math
            physics_score = freq / math.log(energy + 1.1)

            suggestions.append({
                "text": command,
                "confidence": freq / len(matching_records), # Simple confidence score
                "physics_score": physics_score,
                "energy_impact_prediction": energy,
                "mathematical_justification": f"Score based on frequency ({freq}) and energy efficiency ({energy:.2f})."
            })
            processed_commands.add(command)

        # 3. Rank suggestions by the physics score.
        ranked_suggestions = sorted(suggestions, key=lambda s: s["physics_score"], reverse=True)

        return {"suggestions": ranked_suggestions[:10]} # Return top 10
