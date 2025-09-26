import networkx as nx
from datetime import datetime
import uuid
import spacy
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.persistence import PersistenceManager

class ConstellationMemory:
    """
    A knowledge constellation that captures, stores, and retrieves contextual
    information in a graph structure.
    """
    def __init__(self, persistence_manager: Optional['PersistenceManager'] = None, config=None):
        self.config = config or {}
        self.graph = nx.DiGraph()
        self.persistence_manager = persistence_manager

        if self.persistence_manager:
            self._load_from_persistence()

        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Spacy 'en_core_web_sm' model not found. Run 'python -m spacy download en_core_web_sm'")
            self.nlp = None

    def add_fact(self, content: str, fact_type: str, confidence: float = 1.0, access_level: str = "private", owner: str = "system"):
        """
        Adds a fact to the constellation. A fact is a node in the graph.

        Args:
            content (str): The content of the fact.
            fact_type (str): The type of fact (e.g., 'decision', 'observation', 'code_pattern').
            confidence (float): The confidence in the fact's correctness (0.0 to 1.0).
            access_level (str): The access level for the fact.
            owner (str): The owner of the fact.

        Returns:
            str: The unique ID of the new fact node.
        """
        node_id = str(uuid.uuid4())
        self.graph.add_node(
            node_id,
            content=content,
            type=fact_type,
            timestamp=datetime.utcnow(),
            confidence=confidence,
            access_level=access_level,
            owner=owner
        )
        return node_id

    def add_relationship(self, source_id: str, target_id: str, label: str):
        """
        Adds a directed relationship between two facts.

        Args:
            source_id (str): The ID of the source fact node.
            target_id (str): The ID of the target fact node.
            label (str): The label describing the relationship (e.g., 'implies', 'causes', 'related_to').
        """
        if self.graph.has_node(source_id) and self.graph.has_node(target_id):
            self.graph.add_edge(source_id, target_id, label=label, timestamp=datetime.utcnow())
        else:
            raise ValueError("One or both nodes do not exist in the graph.")

    def get_fact(self, node_id: str):
        """Retrieves a fact by its ID."""
        return self.graph.nodes.get(node_id)

    def query(self, query: 'MemoryQuery'):
        """
        Queries the memory using a MemoryQuery object.
        """
        if query.search_mode == "keyword":
            return self._keyword_search(query)
        elif query.search_mode == "semantic":
            return self._semantic_search(query)
        else:
            raise ValueError(f"Unsupported search mode: {query.search_mode}")

    def _keyword_search(self, query: 'MemoryQuery'):
        results = []
        for node_id, data in self.graph.nodes(data=True):
            if self._matches_filters(data, query):
                if query.search_term.lower() in data.get('content', '').lower():
                    results.append((node_id, data))
        results.sort(key=lambda x: (x[1].get('confidence', 0), x[1].get('timestamp')), reverse=True)
        return results[:query.limit]

    def _semantic_search(self, query: 'MemoryQuery'):
        if not self.nlp:
            print("NLP model not available. Falling back to keyword search.")
            return self._keyword_search(query)

        query_doc = self.nlp(query.search_term)
        results = []
        for node_id, data in self.graph.nodes(data=True):
            if self._matches_filters(data, query):
                content = data.get('content', '')
                if content:
                    content_doc = self.nlp(content)
                    similarity = query_doc.similarity(content_doc)
                    if similarity > 0.5:  # Similarity threshold
                        results.append((node_id, data, similarity))

        results.sort(key=lambda x: x[2], reverse=True)
        return [(node_id, data) for node_id, data, sim in results[:query.limit]]

    def _matches_filters(self, node_data: dict, query: 'MemoryQuery') -> bool:
        if not self._check_access(node_data, query.user_id, query.user_roles):
            return False
        if query.fact_types and node_data.get('type') not in query.fact_types:
            return False
        if query.owner and node_data.get('owner') != query.owner:
            return False
        timestamp = node_data.get('timestamp')
        if timestamp:
            if query.start_date and timestamp < query.start_date:
                return False
            if query.end_date and timestamp > query.end_date:
                return False
        return True

    def _check_access(self, node_data: dict, user_id: Optional[str] = None, user_roles: Optional[list] = None) -> bool:
        """
        Checks if a user has access to a given node based on ownership and roles.
        """
        access_level = node_data.get('access_level', 'private')
        owner = node_data.get('owner')

        if access_level == 'public':
            return True

        if user_roles and 'admin' in user_roles:
            return True

        if user_id and owner and user_id == owner:
            return True

        return False

    def learn_from_artifact(self, artifact_type: str, content: str, owner: str = "system"):
        """
        Learns from a given artifact by extracting facts and relationships using NLP.

        Args:
            artifact_type (str): The type of artifact (e.g., 'conversation', 'code_comment').
            content (str): The text content of the artifact.
            owner (str): The owner of the artifact.
        """
        if not self.nlp:
            print("NLP model not available. Cannot learn from artifact.")
            return

        doc = self.nlp(content)

        # Add named entities as facts
        entities = {}
        for ent in doc.ents:
            entity_id = self.add_fact(ent.text, f"entity_{ent.label_.lower()}", owner=owner)
            entities[ent.text] = entity_id

        # Add noun chunks as facts (if they are not already entities)
        for chunk in doc.noun_chunks:
            if chunk.text not in entities:
                chunk_id = self.add_fact(chunk.text, "concept", owner=owner)
                entities[chunk.text] = chunk_id

        # Create relationships based on sentence structure
        for sent in doc.sents:
            sent_entities = [ent.text for ent in sent.ents]
            sent_chunks = [chunk.text for chunk in sent.noun_chunks]

            # Connect all entities and concepts within the same sentence
            items_in_sentence = list(set(sent_entities + sent_chunks))
            for i in range(len(items_in_sentence)):
                for j in range(i + 1, len(items_in_sentence)):
                    source_text = items_in_sentence[i]
                    target_text = items_in_sentence[j]

                    source_id = entities.get(source_text)
                    target_id = entities.get(target_text)

                    if source_id and target_id:
                        # A simple relationship, can be improved with dependency parsing
                        self.add_relationship(source_id, target_id, "related_to")

    def persist(self):
        """Saves the graph to a file using the persistence manager."""
        if self.persistence_manager:
            print("Persisting constellation to disk...")
            self.persistence_manager.save_constellation(self)
        else:
            print("No persistence manager configured. Skipping persistence.")

    def _load_from_persistence(self):
        """Loads the graph from a file using the persistence manager."""
        if self.persistence_manager:
            print("Loading constellation from disk...")
            self.persistence_manager.load_constellation(self)