import unittest
import time
from datetime import datetime, timedelta

from llm.capability_tokens import CapabilityManager, Permission

class TestCapabilityManager(unittest.TestCase):

    def setUp(self):
        self.manager = CapabilityManager()
        self.agent_id = "test-agent-007"
        self.tools = ["read_file", "write_file"]
        self.permissions = {Permission.READ_FILES, Permission.WRITE_FILES}
        self.energy_budget = 100.0

    def test_create_token_successfully(self):
        """Test that a token is created with the correct attributes."""
        token = self.manager.create_token(
            agent_id=self.agent_id,
            allowed_tools=self.tools,
            permissions=self.permissions,
            energy_budget=self.energy_budget,
            ttl_seconds=60
        )
        self.assertEqual(token.agent_id, self.agent_id)
        self.assertEqual(token.allowed_tools, self.tools)
        self.assertEqual(token.permissions, self.permissions)
        self.assertAlmostEqual(
            token.expires_at.timestamp(),
            (datetime.utcnow() + timedelta(seconds=60)).timestamp(),
            delta=1
        )
        self.assertTrue(token.signature)

    def test_validate_valid_token(self):
        """Test that a freshly created token is valid."""
        token = self.manager.create_token(
            agent_id=self.agent_id,
            allowed_tools=self.tools,
            permissions=self.permissions,
            energy_budget=self.energy_budget
        )
        self.assertTrue(self.manager.validate_token(token))

    def test_invalidate_tampered_token(self):
        """Test that a token with altered data is invalid."""
        token = self.manager.create_token(
            agent_id=self.agent_id,
            allowed_tools=self.tools,
            permissions=self.permissions,
            energy_budget=self.energy_budget
        )
        # Tamper with the data after signing
        token.energy_budget = 200.0
        self.assertFalse(self.manager.validate_token(token))

    def test_invalidate_expired_token(self):
        """Test that an expired token is invalid."""
        token = self.manager.create_token(
            agent_id=self.agent_id,
            allowed_tools=self.tools,
            permissions=self.permissions,
            energy_budget=self.energy_budget,
            ttl_seconds=-1 # Expired in the past
        )
        self.assertFalse(self.manager.validate_token(token))

    def test_signature_changes_with_payload(self):
        """Test that the signature changes if the payload changes."""
        token1 = self.manager.create_token(
            agent_id=self.agent_id,
            allowed_tools=["tool1"],
            permissions=self.permissions,
            energy_budget=self.energy_budget
        )
        token2 = self.manager.create_token(
            agent_id=self.agent_id,
            allowed_tools=["tool2"], # Different tool
            permissions=self.permissions,
            energy_budget=self.energy_budget
        )
        self.assertNotEqual(token1.signature, token2.signature)

if __name__ == '__main__':
    unittest.main()
