import asyncio
import logging
from datetime import datetime
from typing import List, NamedTuple, Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from llm.client import LLMClient

log = logging.getLogger(__name__)


class MemoryEntry(NamedTuple):
    """A single entry in the constellation memory."""
    content: str
    embedding: np.ndarray
    timestamp: datetime


class ConstellationMemory:
    """
    A context-aware memory system that stores information as vectors
    and retrieves them based on semantic similarity.
    """

    def __init__(self, llm_client: LLMClient, embedding_model: str = "text-embedding-ada-002"):
        """
        Initializes the ConstellationMemory.

        Args:
            llm_client: An asynchronous LLM client for generating embeddings.
            embedding_model: The name of the embedding model to use.
        """
        self.llm_client = llm_client
        self.embedding_model = embedding_model
        self._memory: List[MemoryEntry] = []
        self._lock = asyncio.Lock()
        log.info("ConstellationMemory initialized.")

    async def add_memory(self, content: str):
        """
        Adds a new piece of information to the memory.

        The content is converted into an embedding and stored along with a timestamp.

        Args:
            content: The text content to store.
        """
        if not content:
            log.warning("Attempted to add empty content to memory.")
            return

        try:
            log.debug(f"Generating embedding for content: '{content[:50]}...'")
            embeddings = await self.llm_client.embed(
                texts=[content], embedding_model=self.embedding_model
            )
            embedding = np.array(embeddings[0])

            async with self._lock:
                entry = MemoryEntry(
                    content=content,
                    embedding=embedding,
                    timestamp=datetime.utcnow()
                )
                self._memory.append(entry)
            log.info(f"Added new memory entry. Total entries: {len(self._memory)}")

        except Exception as e:
            log.error(f"Failed to add memory entry: {e}", exc_info=True)

    async def query(self, query_text: str, top_k: int = 5) -> List[dict]:
        """
        Queries the memory for the most relevant entries based on semantic similarity.

        Args:
            query_text: The query string to search for.
            top_k: The number of most relevant results to return.

        Returns:
            A list of dictionaries, where each dictionary represents a
            relevant memory entry and its similarity score.
        """
        if not self._memory:
            log.warning("Queried empty memory.")
            return []

        try:
            # 1. Generate embedding for the query
            log.debug(f"Generating embedding for query: '{query_text[:50]}...'")
            query_embedding_list = await self.llm_client.embed(
                texts=[query_text], embedding_model=self.embedding_model
            )
            query_embedding = np.array(query_embedding_list[0]).reshape(1, -1)

            async with self._lock:
                # 2. Get all stored embeddings
                stored_embeddings = np.array([entry.embedding for entry in self._memory])
                if stored_embeddings.ndim == 1:
                    stored_embeddings = stored_embeddings.reshape(1, -1)

                # 3. Calculate cosine similarity
                similarities = cosine_similarity(query_embedding, stored_embeddings)[0]

                # 4. Get the top_k results
                top_indices = np.argsort(similarities)[::-1][:top_k]

                results = [
                    {
                        "content": self._memory[i].content,
                        "relevance_score": similarities[i],
                        "timestamp": self._memory[i].timestamp.isoformat(),
                    }
                    for i in top_indices
                ]

            log.info(f"Query returned {len(results)} results.")
            return results

        except Exception as e:
            log.error(f"Failed to query memory: {e}", exc_info=True)
            return []

    def get_all_memories(self) -> List[dict]:
        """Returns all stored memories."""
        return [
            {
                "content": entry.content,
                "timestamp": entry.timestamp.isoformat()
            }
            for entry in self._memory
        ]

    async def clear(self):
        """Clears all entries from the memory."""
        async with self._lock:
            self._memory.clear()
        log.info("ConstellationMemory cleared.")