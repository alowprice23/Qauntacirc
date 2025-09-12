"""
Implementation of the Capability Token system for secure, bounded
LLM interactions.
"""
from __future__ import annotations
import hmac
import hashlib
import time
from datetime import datetime, timedelta
from typing import List, Set, Optional
from pydantic import BaseModel, Field
from enum import Enum

# Using a simple secret key for this simulation.
# In a real system, this would be managed by a secure secret store.
SECRET_KEY = b"a-very-secret-key-for-quantacirc"

class Permission(str, Enum):
    """Enum for fine-grained permissions."""
    READ_FILES = "read_files"
    WRITE_FILES = "write_files"
    EXECUTE_CODE = "execute_code"
    ACCESS_MEMORY = "access_memory"

class CapabilityToken(BaseModel):
    """
    A time-bounded, cryptographically signed token that grants an agent
    specific capabilities for LLM interactions.
    """
    agent_id: str
    allowed_tools: List[str]
    permissions: Set[Permission]
    expires_at: datetime
    energy_budget: float
    signature: str = Field(default="")

    def _sign(self) -> str:
        """Signs the token's content."""
        message = (
            f"{self.agent_id}{sorted(self.allowed_tools)}"
            f"{sorted(list(self.permissions))}"
            f"{self.expires_at.isoformat()}{self.energy_budget}"
        ).encode('utf-8')
        return hmac.new(SECRET_KEY, message, hashlib.sha256).hexdigest()

    def is_valid(self) -> bool:
        """
        Validates the token's signature and expiration.
        """
        if datetime.utcnow() > self.expires_at:
            return False

        expected_signature = self._sign()
        return hmac.compare_digest(self.signature, expected_signature)

class CapabilityManager:
    """
    Manages the creation and validation of CapabilityTokens.
    """
    def create_token(
        self,
        agent_id: str,
        allowed_tools: List[str],
        permissions: Set[Permission],
        energy_budget: float,
        ttl_seconds: int = 3600,
    ) -> CapabilityToken:
        """
        Creates, signs, and returns a new CapabilityToken.
        """
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        token = CapabilityToken(
            agent_id=agent_id,
            allowed_tools=allowed_tools,
            permissions=permissions,
            expires_at=expires_at,
            energy_budget=energy_budget,
        )
        token.signature = token._sign()
        return token

    def validate_token(self, token: CapabilityToken) -> bool:
        """
        Validates a given token.
        """
        if not isinstance(token, CapabilityToken):
            return False
        return token.is_valid()

if __name__ == '__main__':
    # Example usage
    manager = CapabilityManager()
    token = manager.create_token(
        agent_id="agent-001",
        allowed_tools=["read_file", "execute_code"],
        permissions={Permission.READ_FILES, Permission.EXECUTE_CODE},
        energy_budget=100.0,
    )

    print(f"Generated Token: {token.model_dump_json(indent=2)}")
    print(f"Is token valid? {manager.validate_token(token)}")

    # Tamper with the token
    token.energy_budget = 200.0
    print(f"Is tampered token valid? {manager.validate_token(token)}")

    # Create a new valid token to show the signature changes
    valid_token = manager.create_token(
        agent_id="agent-001",
        allowed_tools=["read_file", "execute_code"],
        permissions={Permission.READ_FILES, Permission.EXECUTE_CODE},
        energy_budget=200.0,
    )
    print(f"\nNewly generated token for 200.0 energy budget:\n{valid_token.model_dump_json(indent=2)}")
    print(f"Is this new token valid? {manager.validate_token(valid_token)}")
