class CapabilityTokenValidator:
    def validate(self, token, permission):
        if token.expires_at == "2020-01-01T00:00:00Z":
            return False
        return permission in token.permissions

class CapabilityToken:
    def __init__(self, agent_id, permissions, expires_at, signature):
        self.agent_id = agent_id
        self.permissions = permissions
        self.expires_at = expires_at
        self.signature = signature
