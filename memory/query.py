from __future__ import annotations
from datetime import datetime
from typing import Optional, List

class MemoryQuery:
    """
    Represents a query to the Constellation memory system.
    """
    def __init__(
        self,
        search_term: str,
        search_mode: str = "semantic",  # "semantic" or "keyword"
        fact_types: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        owner: Optional[str] = None,
        limit: int = 10,
        user_id: Optional[str] = None,
        user_roles: Optional[List[str]] = None,
    ):
        self.search_term = search_term
        self.search_mode = search_mode
        self.fact_types = fact_types or []
        self.start_date = start_date
        self.end_date = end_date
        self.owner = owner
        self.limit = limit
        self.user_id = user_id
        self.user_roles = user_roles or []

class QueryBuilder:
    """
    A builder for creating MemoryQuery objects.
    """
    def __init__(self):
        self._search_term: str = ""
        self._search_mode: str = "semantic"
        self._fact_types: Optional[List[str]] = None
        self._start_date: Optional[datetime] = None
        self._end_date: Optional[datetime] = None
        self._owner: Optional[str] = None
        self._limit: int = 10
        self._user_id: Optional[str] = None
        self._user_roles: Optional[List[str]] = None

    def search(self, search_term: str) -> QueryBuilder:
        self._search_term = search_term
        return self

    def mode(self, search_mode: str) -> QueryBuilder:
        if search_mode not in ["semantic", "keyword"]:
            raise ValueError("Search mode must be 'semantic' or 'keyword'.")
        self._search_mode = search_mode
        return self

    def with_types(self, fact_types: List[str]) -> QueryBuilder:
        self._fact_types = fact_types
        return self

    def since(self, start_date: datetime) -> QueryBuilder:
        self._start_date = start_date
        return self

    def until(self, end_date: datetime) -> QueryBuilder:
        self._end_date = end_date
        return self

    def owned_by(self, owner: str) -> QueryBuilder:
        self._owner = owner
        return self

    def limit(self, limit: int) -> QueryBuilder:
        self._limit = limit
        return self

    def as_user(self, user_id: str, roles: Optional[List[str]] = None) -> QueryBuilder:
        self._user_id = user_id
        self._user_roles = roles or []
        return self

    def build(self) -> MemoryQuery:
        if not self._search_term:
            raise ValueError("A search term is required to build a query.")
        return MemoryQuery(
            search_term=self._search_term,
            search_mode=self._search_mode,
            fact_types=self._fact_types,
            start_date=self._start_date,
            end_date=self._end_date,
            owner=self._owner,
            limit=self._limit,
            user_id=self._user_id,
            user_roles=self._user_roles,
        )