import numpy as np
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class NodeType(Enum):
    """Enumeration for types of knowledge nodes."""
    FACT = "fact"
    DECISION = "decision"
    REQUIREMENT = "requirement"
    PROOF = "proof"

@dataclass
class KnowledgeNode:
    """Represents a node in the constellation knowledge graph"""
    id: str
    type: NodeType
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = field(default=None, repr=False)
    created_at: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0

class ConstellationMemory:
    """Manages structured knowledge graph with semantic search"""

    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.node_index: Dict[str, KnowledgeNode] = {}
        self.relation_types: Set[str] = set()

    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate a semantic embedding for a given text."""
        return self.vectorizer.transform([text]).toarray()

    def add_fact(self, fact: str, fact_type: NodeType, metadata: Dict = None) -> str:
        """Add a new fact to the knowledge graph"""
        fact_id = f"{fact_type.value}_{hash(fact)}"

        if fact_id in self.node_index:
            # Fact already exists, we can update confidence or metadata if needed.
            # For now, just return the ID.
            return fact_id

        node = KnowledgeNode(
            id=fact_id,
            type=fact_type,
            content=fact,
            metadata=metadata or {},
            confidence=1.0
        )

        self.node_index[fact_id] = node

        # This is inefficient, but ensures all vectors are in the same space.
        # For larger-scale applications, a more sophisticated embedding
        # update strategy would be needed.
        all_content = [n.content for n in self.node_index.values()]
        self.vectorizer.fit(all_content)

        for n_id, n in self.node_index.items():
            embedding = self._generate_embedding(n.content)
            n.embedding = embedding
            # We need to update the graph node data as well
            if n_id in self.graph:
                self.graph.nodes[n_id]['embedding'] = embedding

        # Add the node to the graph *after* the embedding is generated
        self.graph.add_node(fact_id, **node.__dict__)

        # Automatically infer relationships with existing nodes
        self._infer_relationships(node)

        return fact_id

    def query_facts(self, query: str, limit: int = 10) -> List[KnowledgeNode]:
        """Query facts using semantic similarity and graph traversal"""
        if not self.node_index or not hasattr(self.vectorizer, 'vocabulary_') or not self.vectorizer.vocabulary_:
            return []

        query_embedding = self._generate_embedding(query)

        similarities = []
        for node_id, node in self.node_index.items():
            if node.embedding is not None and node.embedding.any():
                similarity = cosine_similarity(
                    query_embedding.reshape(1, -1),
                    node.embedding.reshape(1, -1)
                )[0][0]
                similarities.append((node, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return [node for node, _ in similarities[:limit]]

    def get_context(self, query: str, max_tokens: int = 8000) -> str:
        """Generate relevant context for LLM prompting"""
        relevant_facts = self.query_facts(query, limit=50)

        context_parts = []
        token_count = 0

        for fact in relevant_facts:
            fact_text = f"[{fact.type.value}] {fact.content}"
            # A simple way to estimate tokens
            fact_tokens = len(fact_text.split())

            if token_count + fact_tokens > max_tokens:
                break

            context_parts.append(fact_text)
            token_count += fact_tokens

            # Add related facts through graph traversal
            related_facts = self._get_related_facts(fact.id, max_depth=2)
            for related in related_facts:
                related_text = f"  └─ Related: [{related.type.value}] {related.content}"
                related_tokens = len(related_text.split())

                if token_count + related_tokens > max_tokens:
                    break

                context_parts.append(related_text)
                token_count += related_tokens

        return "\n".join(context_parts)

    def _get_related_facts(self, node_id: str, max_depth: int) -> List[KnowledgeNode]:
        """Get related facts by traversing the knowledge graph."""
        if node_id not in self.graph:
            return []

        related_node_ids = set()
        # Find neighbors up to max_depth
        if self.graph.has_node(node_id):
            bfs_edges = nx.bfs_edges(self.graph, source=node_id, depth_limit=max_depth)
            for u, v in bfs_edges:
                related_node_ids.add(v)

        return [self.node_index[n_id] for n_id in related_node_ids if n_id in self.node_index]

    def generate_llm_context(self,
                        agent_id: str,
                        current_task: str,
                        max_context_tokens: int = 6000) -> Dict[str, Any]:
        """Generate optimized context for LLM agent interactions"""

        context = {
            "relevant_facts": [],
            "agent_history": [],
            "related_decisions": [],
            "open_obligations": [],
            "mathematical_context": []
        }

        # Get agent-specific history by querying for metadata
        agent_history_nodes = [
            node for node in self.node_index.values()
            if node.metadata.get("agent_id") == agent_id
        ]
        # Sort by creation time to get the most recent history
        agent_history_nodes.sort(key=lambda x: x.created_at, reverse=True)
        context["agent_history"] = [
            f"Previous: {fact.content}"
            for fact in agent_history_nodes[:10]
        ]

        # Get task-relevant facts
        task_facts = self.query_facts(current_task, limit=15)
        context["relevant_facts"] = [
            f"[{fact.type.value}] {fact.content}" for fact in task_facts
        ]

        # Get related mathematical context if keywords are in the task
        math_patterns = ["theorem", "proof", "equation", "bound", "convergence"]
        if any(pattern in current_task.lower() for pattern in math_patterns):
            math_query = " ".join([p for p in math_patterns if p in current_task.lower()])
            math_facts = self.query_facts(math_query, limit=5)
            context["mathematical_context"].extend([
                f"[{fact.type.value}] {fact.content}" for fact in math_facts
            ])

        # Get open obligations (for closure checking)
        obligation_facts = self.query_facts("obligation", limit=10)
        open_obligations = [
            fact for fact in obligation_facts
            if "open" in fact.metadata.get("status", "")
        ]
        context["open_obligations"] = [
            fact.content for fact in open_obligations
        ]

        # Get related decisions
        decision_facts = self.query_facts(f"decision related to {current_task}", limit=5)
        context["related_decisions"] = [
            f"[{fact.type.value}] {fact.content}" for fact in decision_facts
        ]

        # Optimize context length
        formatted_context = self._format_context_for_llm(context)

        if len(formatted_context.split()) > max_context_tokens:
            formatted_context = self._truncate_context(formatted_context, max_context_tokens)

        return {
            "formatted_context": formatted_context,
            "context_components": context,
            "token_count": len(formatted_context.split())
        }

    def _format_context_for_llm(self, context: Dict[str, List[str]]) -> str:
        """Formats the context dictionary into a single string for the LLM."""
        context_str = ""
        for key, items in context.items():
            if items:
                context_str += f"--- {key.replace('_', ' ').upper()} ---\n"
                context_str += "\n".join(items) + "\n\n"
        return context_str.strip()

    def _truncate_context(self, context_str: str, max_tokens: int) -> str:
        """Truncates the context string to a maximum number of tokens."""
        tokens = context_str.split()
        if len(tokens) > max_tokens:
            return " ".join(tokens[:max_tokens])
        return context_str

    def _infer_relationships(self, new_node: KnowledgeNode):
        """Automatically infer relationships with existing nodes"""

        for existing_id, existing_node in self.node_index.items():
            if existing_id == new_node.id:
                continue

            # Compute semantic similarity
            if (new_node.embedding is not None and
                existing_node.embedding is not None and
                new_node.embedding.any() and existing_node.embedding.any()):

                similarity = cosine_similarity(
                    new_node.embedding.reshape(1, -1),
                    existing_node.embedding.reshape(1, -1)
                )[0][0]

                # Add similarity edge if above threshold
                if similarity > 0.7:
                    self.graph.add_edge(
                        new_node.id,
                        existing_id,
                        relation="similar_to",
                        weight=similarity
                    )

            # Infer logical relationships based on content, checking both directions
            # Direction 1: new_node -> existing_node
            logical_relation_1 = self._infer_logical_relation(new_node, existing_node)
            if logical_relation_1:
                self.graph.add_edge(
                    new_node.id,
                    existing_id,
                    relation=logical_relation_1["type"],
                    confidence=logical_relation_1["confidence"]
                )

            # Direction 2: existing_node -> new_node
            logical_relation_2 = self._infer_logical_relation(existing_node, new_node)
            if logical_relation_2:
                self.graph.add_edge(
                    existing_id,
                    new_node.id,
                    relation=logical_relation_2["type"],
                    confidence=logical_relation_2["confidence"]
                )

    def _infer_logical_relation(self,
                              node1: KnowledgeNode,
                              node2: KnowledgeNode) -> Optional[Dict]:
        """Infer logical relationships between nodes"""

        # Check for causality patterns
        causality_patterns = [
            (r"(.*)\s+causes\s+(.*)", "causes"),
            (r"(.*)\s+depends on\s+(.*)", "depends_on"),
            (r"(.*)\s+implements\s+(.*)", "implements"),
            (r"(.*)\s+proves\s+(.*)", "proves")
        ]

        for pattern, relation in causality_patterns:
            if re.search(pattern, node1.content, re.IGNORECASE):
                matches = re.findall(pattern, node1.content, re.IGNORECASE)
                if matches:
                    entity1, entity2 = matches[0]
                    if re.search(r'\b' + re.escape(entity2) + r'\b', node2.content, re.IGNORECASE):
                        return {
                            "type": relation,
                            "confidence": 0.8,
                            "entities": (entity1, entity2)
                        }

        # Check for contradiction patterns
        contradiction_patterns = [
            r"not\s+(\w+)",
            r"(\w+)\s+is\s+false",
            r"(\w+)\s+fails"
        ]

        for pattern in contradiction_patterns:
            match = re.search(pattern, node1.content, re.IGNORECASE)
            if match:
                negated_concept = match.group(1)
                # Check if node2 asserts the opposite, but is not also a negation
                if (re.search(r'\b' + re.escape(negated_concept) + r'\b', node2.content, re.IGNORECASE) and
                    not re.search(r'not\s+' + re.escape(negated_concept), node2.content, re.IGNORECASE)):
                    return {
                        "type": "contradicts",
                        "confidence": 0.9,
                        "concept": negated_concept
                    }

        return None
