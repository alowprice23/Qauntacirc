# agents/pauli_guard/similarity_ops.py
"""
Core operations for similarity detection and code orthogonalization
based on principles from linear algebra and information theory.

This module provides the foundation for the PauliGuard agent's ability
to enforce the principle that no two code modules should occupy the
same semantic state, analogous to the Pauli Exclusion Principle.

⟨ψᵢ|ψⱼ⟩ = 0 for i ≠ j
"""

import zlib
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer

# Placeholder for code normalization functions from ops.py if needed
# from .ops import normalize_code

def ncd_similarity(code1: str, code2: str) -> float:
    """
    Calculates similarity based on Normalized Compression Distance (NCD).
    NCD(x,y) = (Z(xy) - min(Z(x), Z(y))) / max(Z(x), Z(y))
    Similarity = 1 - NCD
    """
    if not code1 and not code2:
        return 1.0
    if not code1 or not code2:
        return 0.0

    z_code1 = len(zlib.compress(code1.encode()))
    z_code2 = len(zlib.compress(code2.encode()))
    z_combined = len(zlib.compress((code1 + code2).encode()))

    ncd = (z_combined - min(z_code1, z_code2)) / max(z_code1, z_code2)
    return 1 - ncd

def vectorize_code(code_blocks: List[str]) -> np.ndarray:
    """
    Converts a list of code blocks into TF-IDF vectors.
    """
    vectorizer = TfidfVectorizer(analyzer='word', token_pattern=r'\b\w+\b')
    vectors = vectorizer.fit_transform(code_blocks)
    return vectors.toarray()

def inner_product(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Computes the inner product (dot product) of two code vectors.
    """
    return np.dot(vec1, vec2)

def gram_schmidt_orthogonalize(code_vectors: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Performs Modified Gram-Schmidt orthogonalization on a set of code vectors.
    This version is more numerically stable.

    Returns a tuple of (orthogonal_basis, transformation_matrix).
    """
    n, m = code_vectors.shape
    orthogonal_basis = np.zeros((n, m))
    transformation_matrix = np.zeros((n, n)) # R matrix in QR decomposition

    vectors = code_vectors.T.copy() # Operate on columns for easier indexing

    for i in range(n):
        v_i = vectors[:, i]
        r_ii = np.linalg.norm(v_i)

        if r_ii < 1e-12:
            # This vector is linearly dependent or zero
            orthogonal_basis[i] = np.zeros(m)
            transformation_matrix[i, i] = 0
            continue

        q_i = v_i / r_ii
        orthogonal_basis[i] = q_i
        transformation_matrix[i, i] = r_ii

        for j in range(i + 1, n):
            v_j = vectors[:, j]
            r_ij = np.dot(q_i, v_j)
            vectors[:, j] = v_j - r_ij * q_i
            transformation_matrix[i, j] = r_ij

    return orthogonal_basis, transformation_matrix

def generate_refactoring_from_orthogonalization(
    original_blocks: Dict[str, str],
    vectorizer: TfidfVectorizer,
    orthogonal_basis: np.ndarray,
    transformation_matrix: np.ndarray
) -> Dict[str, Any]:
    """
    Generates a refactoring plan from the results of Gram-Schmidt.

    This is a conceptual, heuristic-based implementation.
    """
    feature_names = vectorizer.get_feature_names_out()

    # The first basis vector represents the most significant shared component.
    shared_basis_vector = orthogonal_basis[0]

    # Extract the most important features (tokens) from this basis vector.
    # This is a simplification. A real implementation would be more complex.
    important_feature_indices = np.argsort(shared_basis_vector)[::-1]

    # Heuristic: Take the top N tokens to form the "core" of the shared function.
    # This is highly experimental.
    num_core_tokens = 10
    core_tokens = [feature_names[i] for i in important_feature_indices[:num_core_tokens] if shared_basis_vector[i] > 0.1]

    # Another heuristic: Find the original code block that is most similar to the shared basis vector.
    # Use that as the template for the refactored code.
    # This is more robust than just using tokens.

    # We need the original vectors to compare against the basis
    original_vectors = vectorize_code(list(original_blocks.values()))

    similarities = [inner_product(vec, shared_basis_vector) for vec in original_vectors]
    most_similar_idx = np.argmax(similarities)
    template_code = list(original_blocks.values())[most_similar_idx]

    # This is where a more sophisticated model would be needed to actually
    # synthesize the code. For now, we will create a placeholder.
    refactored_code = f"# Shared logic extracted from similar blocks\n"
    refactored_code += f"# Core functionality based on: {', '.join(core_tokens)}\n"
    refactored_code += f"def shared_function(*args, **kwargs):\n"
    refactored_code += f"    # Approximated from the most similar block\n"
    refactored_code += "\n".join([f"    {line}" for line in template_code.splitlines()])


    # Create the replacement plan
    replacement_plan = []
    for i, (file_path, original_code) in enumerate(original_blocks.items()):

        # The transformation matrix tells us how to reconstruct the original vector
        # from the basis. The coefficients for other basis vectors represent the "unique" parts.
        # This is also highly conceptual.

        unique_coeffs = transformation_matrix[i, 1:]

        replacement_plan.append({
            "file_path": file_path,
            "original_block": original_code,
            "replacement_code": f"from src.shared_logic import shared_function\n\n# Call the shared function\n# Unique aspects represented by coeffs: {unique_coeffs}\nshared_function()"
        })

    return {
        "shared_component_path": "src/shared_logic.py",
        "refactored_code": refactored_code,
        "replacement_plan": replacement_plan,
    }
