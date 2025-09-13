import zstandard as zstd
import gzip
import bz2
import lzma
import hashlib
import numpy as np
from collections import Counter
from typing import Dict, Any

from memory.types import Fact, OptimalEncoding

class ShannonEntropyCalculator:
    """Calculates the Shannon entropy of a given data source."""
    def compute(self, data: bytes) -> float:
        """
        Computes the Shannon entropy for the given data.
        Entropy is calculated in bits per byte.
        """
        if not data:
            return 0.0

        counts = Counter(data)
        total_bytes = len(data)
        entropy = 0.0
        for count in counts.values():
            p_x = count / total_bytes
            entropy -= p_x * np.log2(p_x)

        return entropy

class InformationTheoreticEncoder:
    """
    Finds the optimal encoding for knowledge, minimizing description length
    based on information-theoretic principles.
    """
    def __init__(self):
        self.compression_algorithms = ["zstd", "lzma", "bz2", "gzip"]
        self.entropy_calculator = ShannonEntropyCalculator()

    def _compress_with_algorithm(self, data: bytes, algorithm: str) -> bytes:
        """Compresses data using the specified algorithm."""
        if algorithm == "gzip":
            return gzip.compress(data)
        elif algorithm == "bz2":
            return bz2.compress(data)
        elif algorithm == "lzma":
            return lzma.compress(data)
        elif algorithm == "zstd":
            return zstd.compress(data)
        else:
            raise ValueError(f"Unknown compression algorithm: {algorithm}")

    def _verify_compression_bound(self, entropy: float, compressed_size: int, original_size: int) -> Dict[str, Any]:
        """
        Verifies that the compression is reasonably close to the theoretical limit.
        The theoretical limit is H(X) * n bits, where H(X) is entropy in bits/byte.
        """
        theoretical_limit_bytes = (entropy * original_size) / 8.0

        # We allow for some overhead, as practical compressors have headers and other metadata.
        # A simple check is to see if the compressed size is not excessively larger than the limit.
        is_verified = compressed_size < theoretical_limit_bytes * 1.5 + 100 # 50% margin + 100 bytes fixed overhead

        return {
            "verified": is_verified,
            "theoretical_limit_bytes": theoretical_limit_bytes,
            "actual_compressed_bytes": compressed_size,
            "details": f"Entropy={entropy:.4f} bits/byte. Theoretical limit: {theoretical_limit_bytes:.2f} bytes. Actual: {compressed_size} bytes."
        }

    def _generate_optimality_proof(self, compression_results: Dict[str, Any], optimal_algorithm: str) -> Dict[str, Any]:
        """Generates a proof of optimality by showing the results of all tested algorithms."""
        proof = {
            "optimal_algorithm": optimal_algorithm,
            "reason": "Selected algorithm with the minimum compressed size.",
            "results": {
                alg: {"size": res["size"], "ratio": f"{res['ratio']:.4f}"}
                for alg, res in compression_results.items()
            }
        }
        return proof

    def encode(self, fact: Fact) -> OptimalEncoding:
        """
        Finds the optimal encoding for a fact by selecting the best compression algorithm.
        """
        knowledge_bytes = fact.model_dump_json().encode('utf-8')
        if not knowledge_bytes:
            return OptimalEncoding(
                algorithm='none',
                compressed_data=b'',
                compression_ratio=1.0,
                entropy=0.0,
                bound_verification={"verified": True, "details": "empty content"},
                optimality_proof={"reason": "No data to compress"},
                hash=hashlib.sha256(b'').hexdigest()
            )

        # Entropy is in bits per byte
        entropy = self.entropy_calculator.compute(knowledge_bytes)

        compression_results = {}
        for algorithm in self.compression_algorithms:
            compressed_data = self._compress_with_algorithm(knowledge_bytes, algorithm)
            compression_results[algorithm] = {
                "size": len(compressed_data),
                "ratio": len(compressed_data) / len(knowledge_bytes) if len(knowledge_bytes) > 0 else 1.0,
                "data": compressed_data,
            }

        optimal_algorithm = min(compression_results, key=lambda alg: compression_results[alg]["size"])
        optimal_result = compression_results[optimal_algorithm]

        bound_verification = self._verify_compression_bound(
            entropy, optimal_result["size"], len(knowledge_bytes)
        )

        encoding_hash = hashlib.sha256(optimal_result['data']).hexdigest()

        return OptimalEncoding(
            algorithm=optimal_algorithm,
            compressed_data=optimal_result["data"],
            compression_ratio=optimal_result["ratio"],
            entropy=entropy,
            bound_verification=bound_verification,
            optimality_proof=self._generate_optimality_proof(compression_results, optimal_algorithm),
            hash=encoding_hash,
        )
