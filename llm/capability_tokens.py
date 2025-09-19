import time
import hmac
import hashlib
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class CapabilityToken:
    """Cryptographically signed capability token for LLM tool access"""
    agent_id: str
    allowed_tools: List[str]
    permissions: Dict[str, Any]
    expires_at: float
    signature: str


class CapabilityTokenManager:
    """Manages capability tokens for LLM tool access"""

    def __init__(self, secret_key: bytes):
        self.secret_key = secret_key
        self.active_tokens: Dict[str, CapabilityToken] = {}

    def issue_token(self,
                   agent_id: str,
                   requested_tools: List[str],
                   duration_minutes: int = 60) -> CapabilityToken:
        """Issue a new capability token with specified permissions"""
        allowed_tools = self._validate_tool_requests(agent_id, requested_tools)
        expires_at = time.time() + (duration_minutes * 60)

        # Sort tools to ensure a consistent payload for the signature
        sorted_tools = sorted(allowed_tools)
        payload = f"{agent_id}:{','.join(sorted_tools)}:{expires_at}"
        signature = self._generate_signature(payload)

        token = CapabilityToken(
            agent_id=agent_id,
            allowed_tools=allowed_tools,
            permissions=self._get_agent_permissions(agent_id),
            expires_at=expires_at,
            signature=signature,
        )

        self.active_tokens[token.signature] = token
        return token

    def revoke_token(self, token_signature: str) -> bool:
        """Revoke an active capability token"""
        if token_signature in self.active_tokens:
            del self.active_tokens[token_signature]
            return True
        return False

    def validate_tool_access(self, token: CapabilityToken, tool_name: str) -> bool:
        """Validate that token allows access to specified tool"""
        if token.signature not in self.active_tokens:
            return False

        if not self.is_token_valid(token):
            return False

        return tool_name in token.allowed_tools

    def is_token_valid(self, token: CapabilityToken) -> bool:
        """Verify token signature and expiration."""
        if time.time() >= token.expires_at:
            return False

        payload = f"{token.agent_id}:{','.join(sorted(token.allowed_tools))}:{token.expires_at}"
        expected_signature = self._generate_signature(payload)

        return hmac.compare_digest(token.signature, expected_signature)

    def _generate_signature(self, payload: str) -> str:
        """Generates an HMAC-SHA256 signature."""
        return hmac.new(self.secret_key, payload.encode('utf-8'), hashlib.sha256).hexdigest()

    def _validate_tool_requests(self, agent_id: str, requested_tools: List[str]) -> List[str]:
        """
        Placeholder for validating requested tools against agent's permissions.
        In a real system, this would look up agent permissions from a database or config.
        For now, we'll allow all requested tools.
        """
        # Example of how it could work:
        # agent_perms = self._get_agent_permissions(agent_id)
        # permitted_tools = agent_perms.get("allowed_tools", [])
        # return [tool for tool in requested_tools if tool in permitted_tools]
        return requested_tools

    def _get_agent_permissions(self, agent_id: str) -> Dict[str, Any]:
        """
        Placeholder for fetching agent-specific permissions.
        """
        # In a real system, this would be fetched from a permissions store.
        return {"level": "standard", "max_requests_per_hour": 1000}
