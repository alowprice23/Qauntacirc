import pytest
import hashlib
import json
from datetime import datetime, timedelta, timezone

import nacl.signing
import nacl.encoding
from nacl.exceptions import BadSignatureError

from core.security import (
    Artifact,
    CapabilityBasedSecurityEngine,
    CapabilityToken,
    CapabilityVerification,
    CryptographicProof,
    CryptographicProofEngine,
    ImmutableAuditTrailSystem,
    MathematicalSecurityVerifier,
    MathematicalSecurityVerification,
    QuantumCryptographicSecurityFramework,
    SBOMDependency,
    SBOMRequirement,
    SupplyChainIntegrityVerifier,
    SupplyChainVerification,
    SystemOperation,
)

# --- Test Data and Helpers ---

@pytest.fixture
def signing_key():
    """Provides a NaCL signing key."""
    return nacl.signing.SigningKey.generate()

@pytest.fixture
def verify_key(signing_key):
    """Provides a NaCL verify key corresponding to the signing key."""
    return signing_key.verify_key

def create_capability_token(signing_key, capabilities, expiry_delta=timedelta(days=1)) -> str:
    """Helper to create and sign a capability token."""
    public_key_hex = signing_key.verify_key.encode(encoder=nacl.encoding.HexEncoder).decode('utf-8')
    token = CapabilityToken(
        granted_capabilities=capabilities,
        expiry=datetime.now(timezone.utc) + expiry_delta,
        public_key=public_key_hex,
    )
    signed = signing_key.sign(token.to_signed_message())
    token.signature = signed.signature.hex()
    return token.model_dump_json()

@pytest.fixture
def sample_artifacts():
    """Provides sample artifacts for testing."""
    content1 = b"This is artifact 1."
    content2 = b"This is artifact 2."
    return [
        Artifact(name="artifact1", content=content1, digest=hashlib.sha256(content1).hexdigest(), sbom=[SBOMDependency(name="dep1", version="1.0", license="MIT")]),
        Artifact(name="artifact2", content=content2, digest=hashlib.sha256(content2).hexdigest(), sbom=[SBOMDependency(name="dep2", version="2.0", license="Apache-2.0")]),
    ]

@pytest.fixture
def sample_system_operation(signing_key, sample_artifacts):
    """Provides a sample SystemOperation for testing."""
    token = create_capability_token(signing_key, ["read", "write"])

    artifact_signatures = {
        artifact.name: signing_key.sign(artifact.content).signature.hex()
        for artifact in sample_artifacts
    }

    return SystemOperation(
        operation_name="test_op",
        required_capabilities=["read"],
        capability_tokens=[token],
        mathematical_security_constraints=["(=> read write)"],
        artifacts=sample_artifacts,
        sbom_requirements=SBOMRequirement(allowed_licenses=["MIT", "Apache-2.0"], blocked_packages=[]),
        artifact_signatures=artifact_signatures,
    )

# --- Test Classes ---

@pytest.mark.asyncio
class TestCapabilityBasedSecurityEngine:
    async def test_verify_capabilities_success(self, signing_key):
        engine = CapabilityBasedSecurityEngine()
        token = create_capability_token(signing_key, ["read", "write"])
        result = await engine.verify_comprehensive_capabilities(
            operation_capabilities=["read"],
            provided_tokens=[token],
            mathematical_constraints=["(=> read write)"]
        )
        assert result.verified
        assert result.reason == "All capabilities verified."
        assert result.granted_capabilities == {"read", "write"}

    async def test_verify_capabilities_missing_token(self):
        engine = CapabilityBasedSecurityEngine()
        result = await engine.verify_comprehensive_capabilities(
            operation_capabilities=["read"],
            provided_tokens=[],
            mathematical_constraints=[]
        )
        assert not result.verified
        assert result.reason == "No capability tokens provided."

    async def test_verify_capabilities_bad_signature(self, signing_key):
        engine = CapabilityBasedSecurityEngine()
        token_str = create_capability_token(signing_key, ["read"])
        token_dict = json.loads(token_str)
        token_dict['signature'] = ('0' * 128)
        invalid_token_str = json.dumps(token_dict)

        result = await engine.verify_comprehensive_capabilities(
            operation_capabilities=["read"],
            provided_tokens=[invalid_token_str],
            mathematical_constraints=[]
        )
        assert not result.verified
        assert result.reason == "Invalid signature on capability token."

    async def test_verify_capabilities_expired(self, signing_key):
        engine = CapabilityBasedSecurityEngine()
        token = create_capability_token(signing_key, ["read"], expiry_delta=timedelta(days=-1))
        result = await engine.verify_comprehensive_capabilities(
            operation_capabilities=["read"],
            provided_tokens=[token],
            mathematical_constraints=[]
        )
        assert not result.verified
        assert result.reason == "Capability token has expired."

    async def test_verify_capabilities_missing_capability(self, signing_key):
        engine = CapabilityBasedSecurityEngine()
        token = create_capability_token(signing_key, ["read"])
        result = await engine.verify_comprehensive_capabilities(
            operation_capabilities=["write"],
            provided_tokens=[token],
            mathematical_constraints=[]
        )
        assert not result.verified
        assert result.reason == "Missing capabilities: write"

    async def test_verify_capabilities_unsat_constraints(self, signing_key):
        engine = CapabilityBasedSecurityEngine()
        token = create_capability_token(signing_key, ["read"])
        result = await engine.verify_comprehensive_capabilities(
            operation_capabilities=["read"],
            provided_tokens=[token],
            mathematical_constraints=["(not read)"]
        )
        assert not result.verified
        assert result.reason == "Mathematical security constraints are unsatisfiable."

@pytest.mark.asyncio
class TestSupplyChainIntegrityVerifier:
    async def test_verify_supply_chain_success(self, signing_key, sample_artifacts, sample_system_operation):
        verifier = SupplyChainIntegrityVerifier()
        result = await verifier.verify_complete_supply_chain_integrity(
            artifacts=sample_artifacts,
            sbom_requirements=sample_system_operation.sbom_requirements,
            cryptographic_signatures=sample_system_operation.artifact_signatures,
            provided_tokens=sample_system_operation.capability_tokens,
        )
        assert result.verified
        assert result.reason == "Supply chain integrity verified."

    async def test_verify_supply_chain_digest_mismatch(self, signing_key, sample_artifacts, sample_system_operation):
        verifier = SupplyChainIntegrityVerifier()
        sample_artifacts[0].digest = "invalid_digest"
        result = await verifier.verify_complete_supply_chain_integrity(
            artifacts=sample_artifacts,
            sbom_requirements=sample_system_operation.sbom_requirements,
            cryptographic_signatures=sample_system_operation.artifact_signatures,
            provided_tokens=sample_system_operation.capability_tokens,
        )
        assert not result.verified
        assert "Digest mismatch" in result.reason

    async def test_verify_supply_chain_bad_signature(self, signing_key, sample_artifacts, sample_system_operation):
        verifier = SupplyChainIntegrityVerifier()
        sample_system_operation.artifact_signatures["artifact1"] = ('00' * 64)
        result = await verifier.verify_complete_supply_chain_integrity(
            artifacts=sample_artifacts,
            sbom_requirements=sample_system_operation.sbom_requirements,
            cryptographic_signatures=sample_system_operation.artifact_signatures,
            provided_tokens=sample_system_operation.capability_tokens,
        )
        assert not result.verified
        assert "Invalid signature for artifact" in result.reason

    async def test_verify_supply_chain_blocked_package(self, signing_key, sample_artifacts, sample_system_operation):
        verifier = SupplyChainIntegrityVerifier()
        sample_system_operation.sbom_requirements.blocked_packages = ["dep1"]
        result = await verifier.verify_complete_supply_chain_integrity(
            artifacts=sample_artifacts,
            sbom_requirements=sample_system_operation.sbom_requirements,
            cryptographic_signatures=sample_system_operation.artifact_signatures,
            provided_tokens=sample_system_operation.capability_tokens,
        )
        assert not result.verified
        assert "blocked dependency" in result.reason

    async def test_verify_supply_chain_unallowed_license(self, signing_key, sample_artifacts, sample_system_operation):
        verifier = SupplyChainIntegrityVerifier()
        sample_system_operation.sbom_requirements.allowed_licenses = ["MIT"]
        result = await verifier.verify_complete_supply_chain_integrity(
            artifacts=sample_artifacts,
            sbom_requirements=sample_system_operation.sbom_requirements,
            cryptographic_signatures=sample_system_operation.artifact_signatures,
            provided_tokens=sample_system_operation.capability_tokens,
        )
        assert not result.verified
        assert "unallowed license" in result.reason

@pytest.mark.asyncio
class TestCryptographicProofEngine:
    async def test_generate_proofs_success(self, sample_system_operation):
        engine = CryptographicProofEngine()
        capability_verification = CapabilityVerification(verified=True, granted_capabilities={"read", "write"})
        proofs = await engine.generate_comprehensive_security_proofs(
            operation=sample_system_operation,
            capability_verification=capability_verification,
            supply_chain_verification=SupplyChainVerification(verified=True)
        )
        assert len(proofs) == 1
        assert "comprehensive_proof" in proofs[0].proof_id
        assert "declare-const read" in proofs[0].proof_data
        assert "declare-const write" in proofs[0].proof_data

    async def test_generate_proofs_failure(self, sample_system_operation):
        engine = CryptographicProofEngine()
        proofs = await engine.generate_comprehensive_security_proofs(
            operation=sample_system_operation,
            capability_verification=CapabilityVerification(verified=False),
            supply_chain_verification=SupplyChainVerification(verified=True)
        )
        assert len(proofs) == 0

@pytest.mark.asyncio
class TestImmutableAuditTrailSystem:
    async def test_create_audit_record(self, sample_system_operation):
        system = ImmutableAuditTrailSystem()
        record = await system.create_comprehensive_audit_record(
            operation=sample_system_operation,
            security_verifications=[],
            cryptographic_proofs=[],
            mathematical_security_certificate="cert"
        )
        assert record.record_id
        assert record.record_id == record.immutable_id

@pytest.mark.asyncio
class TestMathematicalSecurityVerifier:
    async def test_verify_properties_sat(self):
        verifier = MathematicalSecurityVerifier()
        proofs = [CryptographicProof(proof_id="p1", proof_data="(declare-const a Bool)\n(assert a)", description="a is true")]
        result = await verifier.verify_mathematical_security_properties(None, proofs, None)
        assert result.verified
        assert "consistent and hold" in result.reason

    async def test_verify_properties_unsat(self):
        verifier = MathematicalSecurityVerifier()
        proofs = [CryptographicProof(proof_id="p1", proof_data="(declare-const a Bool)\n(assert a)\n(assert (not a))", description="contradiction")]
        result = await verifier.verify_mathematical_security_properties(None, proofs, None)
        assert not result.verified
        assert "Contradiction" in result.reason

@pytest.mark.asyncio
class TestQuantumCryptographicSecurityFramework:
    async def test_secure_operation_success(self, sample_system_operation):
        framework = QuantumCryptographicSecurityFramework()
        result = await framework.secure_complete_system_operation(sample_system_operation)
        assert result.operation_security_approved
        assert result.capability_verification.verified
        assert result.supply_chain_verification.verified
        assert result.mathematical_security_verification.verified

    async def test_secure_operation_capability_failure(self, sample_system_operation):
        framework = QuantumCryptographicSecurityFramework()
        sample_system_operation.required_capabilities.append("admin") # Add a capability the token doesn't have
        result = await framework.secure_complete_system_operation(sample_system_operation)
        assert not result.operation_security_approved
        assert not result.capability_verification.verified
        supply_chain_verifier = SupplyChainIntegrityVerifier()
        supply_chain_result = await supply_chain_verifier.verify_complete_supply_chain_integrity(
            artifacts=sample_system_operation.artifacts,
            sbom_requirements=sample_system_operation.sbom_requirements,
            cryptographic_signatures=sample_system_operation.artifact_signatures,
            provided_tokens=sample_system_operation.capability_tokens,
        )
        assert supply_chain_result.verified
        assert not result.cryptographic_proofs
        assert result.mathematical_security_verification.verified
