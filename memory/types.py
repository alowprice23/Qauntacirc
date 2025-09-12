"""
This file contains the core data structures for the constellation memory system.
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field
import numpy as np

class FactType(str, Enum):
    """The type of a fact."""
    PROPOSITION = "PROPOSITION"
    PATTERN = "PATTERN"
    RELATIONSHIP = "RELATIONSHIP"

class RelationshipType(str, Enum):
    """The type of a relationship between knowledge nodes."""
    IMPLIES = "IMPLIES"
    CAUSES = "CAUSES"
    CORRELATES_WITH = "CORRELATES_WITH"
    SUBCLASS_OF = "SUBCLASS_OF"
    INSTANCE_OF = "INSTANCE_OF"

class Knowledge(BaseModel):
    """Base model for a piece of knowledge."""
    content: Any
    initial_confidence: float = 1.0

class Fact(Knowledge):
    """A fact is a piece of knowledge with mathematical properties."""
    type: FactType
    mathematical_properties: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    confidence: float = 1.0
    generalization_proof: Optional[str] = None

class ConstellationConfig(BaseModel):
    """Configuration for the ConstellationMemory."""
    neo4j_uri: str
    embedding_dimension: int
    database_path: str

class ConstellationQuery(BaseModel):
    """A query to the ConstellationMemory."""
    text: str
    filters: Dict[str, Any] = Field(default_factory=dict)
    mathematical_filters: Dict[str, Any] = Field(default_factory=dict)
    relationship_filters: List[str] = Field(default_factory=list)
    max_results: int = 10
    similarity_threshold: float = 0.7
    max_depth: int = 3

    def compute_hash(self) -> str:
        """Computes a hash for the query."""
        import hashlib
        return hashlib.sha256(self.model_dump_json().encode()).hexdigest()

class Intent(BaseModel):
    """Represents an agent's intent."""
    description: str

class Plan(BaseModel):
    """Represents an agent's plan."""
    steps: List[str]

class ExecutionResult(BaseModel):
    """The result of executing a plan."""
    success: bool
    confidence: float
    success_metrics: Dict[str, float]
    energy_delta: float
    convergence_metrics: Dict[str, float]

class OptimalEncoding(BaseModel):
    """Represents the optimal encoding of a piece of knowledge."""
    algorithm: str
    compressed_data: bytes
    compression_ratio: float
    entropy: float
    bound_verification: Any
    optimality_proof: Any
    hash: str

class FactNode(BaseModel):
    """A node in the knowledge graph representing a fact."""
    id: str
    fact: Fact
    encoding: OptimalEncoding
    embedding: np.ndarray
    storage_locations: Dict[str, Any]
    mathematical_certificate: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

class ConsistencyResult(BaseModel):
    """The result of a consistency check."""
    consistent: bool
    proof: Optional[str] = None
    violations: List[str] = Field(default_factory=list)
    confidence: Optional[float] = None
    suggested_resolution: Optional[str] = None
    valid: Optional[bool] = None  # For QuantumKnowledgeGraph compatibility

class LearningResult(BaseModel):
    """The result of a learning operation."""
    pattern_node: Optional[FactNode] = None
    generalization: Optional[Any] = None
    learning_confidence: Optional[float] = None
    mathematical_certificate: Optional[str] = None
    error: Optional[str] = None
    suggested_resolution: Optional[str] = None

class ConstellationResult(BaseModel):
    """The result of a query to the ConstellationMemory."""
    facts: List[FactNode]
    query_hash: str
    mathematical_consistency: Any
    information_content: float
    retrieval_proof: str

class KnowledgeNode(BaseModel):
    """A generic node in the knowledge graph."""
    id: str
    knowledge: Knowledge
    mathematical_properties: Dict[str, Any]
    semantic_signature: str
    creation_timestamp: datetime
    access_count: int
    confidence_score: float
    embedding_vector: np.ndarray

    class Config:
        arbitrary_types_allowed = True

class Relationship(BaseModel):
    """A relationship between two knowledge nodes."""
    type: RelationshipType
    properties: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeEdge(BaseModel):
    """An edge in the knowledge graph representing a relationship."""
    id: str
    source_id: str
    target_id: str
    relationship: Relationship
    mathematical_certificate: str
    strength: float
    creation_timestamp: datetime

class QueryConstraints(BaseModel):
    """Constraints for a graph traversal query."""
    # This can be expanded with specific constraints.
    pass

class KnowledgePath(BaseModel):
    """A path through the knowledge graph."""
    paths: List[List[Union[KnowledgeNode, KnowledgeEdge]]]
    optimization_proof: str
    information_content: float

class VectorID(BaseModel):
    """A unique identifier for a vector in the vector space."""
    id: int

class VectorMetadata(BaseModel):
    """Metadata associated with a vector."""
    fact_id: str
    type: str
    timestamp: str
    mathematical_hash: str

class VectorMatch(BaseModel):
    """A match found during a vector search."""
    vector_id: VectorID
    similarity: float
    metadata: VectorMetadata
    mathematical_certificate: str

class VectorSearchResult(BaseModel):
    """The result of a vector search."""
    matches: List[VectorMatch]
    query_hash: str
    mathematical_bounds: Any
    information_content: float

class OptimizationItem(BaseModel):
    """An item to be considered in an optimization problem."""
    id: str
    value: float
    weight: int
    fact: Fact

class TokenConstraint(BaseModel):
    """A constraint on the number of tokens."""
    max_tokens: int

class OptimizationProblem(BaseModel):
    """An optimization problem for context assembly."""
    objective: str
    items: List[OptimizationItem]
    constraints: List[Any] # Can be a list of different constraint types
    mathematical_formulation: str

class OptimizationSolution(BaseModel):
    """The solution to an optimization problem."""
    selected_facts: List[Fact]
    total_information: float
    optimality_proof: str

class AssembledContext(BaseModel):
    """Context assembled from a set of facts."""
    text: str
    selected_facts: List[Fact]

class OptimizedContext(BaseModel):
    """An optimized context for an agent."""
    context_text: str
    selected_facts: List[Fact]
    information_content: float
    token_usage: int
    mathematical_consistency: Any
    optimization_proof: str

class PersistenceResult(BaseModel):
    """The result of a memory persistence operation."""
    success: bool
    backup_id: str
    integrity_hash: str
    mathematical_verification: Any
