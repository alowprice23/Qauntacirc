import hashlib
import json
from typing import Optional, Dict, Any

class ProofCache:
    """
    A cache for storing and retrieving proof verification results.

    This helps to avoid re-running expensive proof validations for code
    and properties that have already been checked.
    """
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _generate_key(self, property_id: str, code: str) -> str:
        """
        Generates a stable cache key from a property ID and the code content.
        """
        hasher = hashlib.sha256()
        hasher.update(property_id.encode('utf-8'))
        hasher.update(code.encode('utf-8'))
        return hasher.hexdigest()

    def get(self, property_id: str, code: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a proof result from the cache.

        Args:
            property_id: The unique identifier of the property being checked.
            code: The source code associated with the proof.

        Returns:
            The cached result dictionary, or None if not found.
        """
        key = self._generate_key(property_id, code)
        return self._cache.get(key)

    def put(self, property_id: str, code: str, result: Dict[str, Any]):
        """
        Stores a proof result in the cache.

        Args:
            property_id: The unique identifier of the property.
            code: The source code associated with the proof.
            result: The result dictionary to cache.
        """
        key = self._generate_key(property_id, code)
        self._cache[key] = result

    def load(self, path: str):
        """Loads the cache from a JSON file."""
        try:
            with open(path, 'r') as f:
                self._cache = json.load(f)
        except FileNotFoundError:
            pass # It's okay if the cache file doesn't exist yet.
        except json.JSONDecodeError:
            pass # Handle corrupted cache file.

    def save(self, path: str):
        """Saves the cache to a JSON file."""
        with open(path, 'w') as f:
            json.dump(self._cache, f, indent=2)

# Example Usage:
if __name__ == '__main__':
    cache = ProofCache()

    # Define a sample property and code
    code_v1 = "def add(a, b): return a + b"
    property_1 = "add(2, 2) == 4"
    result_1 = {"status": "proved", "engine": "smt"}

    # Put into cache
    cache.put(property_1, code_v1, result_1)
    print(f"Cached result for property '{property_1}' on code_v1")

    # Get from cache
    retrieved_result = cache.get(property_1, code_v1)
    print(f"Retrieved result: {retrieved_result}")
    assert retrieved_result == result_1

    # A different code version should not hit the cache
    code_v2 = "def add(a, b): return a + b + 0"
    miss_result = cache.get(property_1, code_v2)
    print(f"Cache miss for code_v2: {miss_result}")
    assert miss_result is None

    # Save and load cache
    cache.save("proof_cache.json")
    print("Cache saved to 'proof_cache.json'")

    new_cache = ProofCache()
    new_cache.load("proof_cache.json")
    retrieved_result_new = new_cache.get(property_1, code_v1)
    print(f"Retrieved from new cache instance: {retrieved_result_new}")
    assert retrieved_result_new == result_1

    import os
    os.remove("proof_cache.json")
    print("Cleaned up 'proof_cache.json'")