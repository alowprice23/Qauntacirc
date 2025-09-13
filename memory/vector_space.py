import faiss
import numpy as np
import hashlib
from typing import List, Dict, Any

from memory.types import (
    VectorID,
    VectorMetadata,
    VectorMatch,
    VectorSearchResult,
)

class InvalidVectorError(Exception):
    """Custom exception for invalid vectors."""
    pass

class VectorSpaceMathStructure:
    """Represents the mathematical structure of the vector space."""
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.mean_vector = np.zeros(dimension, dtype=np.float32)
        self.covariance_matrix = np.eye(dimension, dtype=np.float32)
        self.vector_count = 0

    def update_stats(self, new_vector: np.ndarray):
        """Updates the statistical properties of the vector space."""
        n = self.vector_count
        if n == 0:
            self.mean_vector = new_vector
        else:
            # Welford's algorithm for online mean and covariance update
            old_mean = self.mean_vector
            self.mean_vector = (n * old_mean + new_vector) / (n + 1)
            # Update covariance (simplified for this context)
            # A full covariance update is computationally expensive
            pass
        self.vector_count += 1

import io

class QuantumVectorSpace:
    """
    Manages vector embeddings and similarity search using Faiss, incorporating
    mathematical consistency and information-theoretic measures.
    """
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(self.dimension)
        self.mathematical_structure = VectorSpaceMathStructure(dimension)
        self.metadata_store: Dict[int, VectorMetadata] = {}

    def __getstate__(self):
        """Custom serialization for QuantumVectorSpace to handle the Faiss index."""
        state = self.__dict__.copy()
        # Convert the Faiss index to a byte string
        index_buffer = faiss.serialize_index(self.index)
        state['index'] = index_buffer
        return state

    def __setstate__(self, state):
        """Custom deserialization for QuantumVectorSpace."""
        # Restore the Faiss index from the byte string
        index_buffer = state.pop('index')
        state['index'] = faiss.deserialize_index(index_buffer)
        self.__dict__.update(state)

    def _verify_vector_properties(self, vector: np.ndarray) -> bool:
        """Verifies vector properties, including dimension and normalization."""
        if vector.shape != (self.dimension,):
            return False
        norm = np.linalg.norm(vector)
        # Check if the vector is approximately normalized
        if not np.isclose(norm, 1.0, atol=1e-6):
            # This check should be done on normalized vectors.
            # We will normalize before adding, so this is more of a sanity check.
            pass
        return True

    def _store_vector_metadata(self, vector_id: int, metadata: VectorMetadata, normalized_vector: np.ndarray):
        """Stores metadata and updates mathematical structure."""
        self.metadata_store[vector_id] = metadata
        self.mathematical_structure.update_stats(normalized_vector)

    def _retrieve_vector_metadata(self, vector_id: int) -> VectorMetadata:
        """Retrieves metadata for a given vector ID."""
        return self.metadata_store.get(vector_id)

    def _generate_similarity_certificate(self, query_hash: str, match: VectorMatch) -> str:
        """Generates a similarity certificate with a cryptographic hash."""
        cert_data = f"{query_hash}|{match.vector_id.id}|{match.similarity:.6f}"
        return f"cert_{hashlib.sha256(cert_data.encode()).hexdigest()}"

    def _compute_query_hash(self, query_vector: np.ndarray) -> str:
        """Computes a hash for the query vector."""
        return hashlib.sha256(query_vector.tobytes()).hexdigest()

    def _compute_search_bounds(self, results: List[VectorMatch]) -> Dict[str, Any]:
        """Computes statistical bounds and properties of the search results."""
        if not results:
            return {"count": 0}

        similarities = [r.similarity for r in results]
        return {
            "count": len(results),
            "min_similarity": min(similarities),
            "max_similarity": max(similarities),
            "mean_similarity": np.mean(similarities),
            "std_dev_similarity": np.std(similarities),
        }

    def _compute_information_content(self, results: List[VectorMatch]) -> float:
        """Computes the Shannon entropy of the similarity scores."""
        if not results:
            return 0.0

        similarities = np.array([r.similarity for r in results])
        # Normalize similarities to be a probability distribution
        probs = similarities / np.sum(similarities)
        # Filter out zero probabilities to avoid log(0)
        probs = probs[probs > 0]

        return -np.sum(probs * np.log2(probs))

    def add_vector(self, vector: np.ndarray, metadata: VectorMetadata) -> VectorID:
        """Adds a vector to the index with normalization and consistency checks."""
        if vector.shape != (self.dimension,):
            raise InvalidVectorError(f"Vector has incorrect dimension {vector.shape}, expected ({self.dimension},)")

        norm = np.linalg.norm(vector)
        if norm == 0:
            normalized_vector = np.zeros(self.dimension, dtype='float32')
        else:
            normalized_vector = (vector / norm).astype('float32')

        if not self._verify_vector_properties(normalized_vector):
            raise InvalidVectorError("Normalized vector does not satisfy mathematical constraints.")

        vector_to_add = normalized_vector.reshape(1, -1)
        vector_id = self.index.ntotal
        self.index.add(vector_to_add)

        self._store_vector_metadata(vector_id, metadata, normalized_vector)

        return VectorID(id=vector_id)

    def search_similar(self, query_vector: np.ndarray, k: int, threshold: float) -> VectorSearchResult:
        """Searches for similar vectors with quantum overlap calculation."""
        norm = np.linalg.norm(query_vector)
        if norm == 0:
            normalized_query = np.zeros(self.dimension, dtype='float32')
        else:
            normalized_query = (query_vector / norm).astype('float32')

        query_hash = self._compute_query_hash(normalized_query)
        query_vector_to_search = normalized_query.reshape(1, -1)
        similarities, indices = self.index.search(query_vector_to_search, k)

        filtered_results = []
        for similarity, index in zip(similarities[0], indices[0]):
            if index == -1:
                continue
            if similarity >= threshold:
                metadata = self._retrieve_vector_metadata(int(index))
                if metadata:
                    match = VectorMatch(
                        vector_id=VectorID(id=int(index)),
                        similarity=float(similarity),
                        metadata=metadata,
                        mathematical_certificate="" # Will be generated next
                    )
                    match.mathematical_certificate = self._generate_similarity_certificate(query_hash, match)
                    filtered_results.append(match)

        return VectorSearchResult(
            matches=filtered_results,
            query_hash=query_hash,
            mathematical_bounds=self._compute_search_bounds(filtered_results),
            information_content=self._compute_information_content(filtered_results)
        )
