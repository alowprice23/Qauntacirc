import asyncio
import os
import sys
import pprint
from typing import List
from datetime import datetime, timedelta, timezone
import nacl.signing
import nacl.encoding
import hashlib
import json

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from the new implementation in src/
from src.quantum_security import (
    QuantumCryptographicSecurityFramework,
    SystemOperation,
    CapabilityToken,
    Artifact,
    SBOMDependency,
    SBOMRequirement,
)

# --- Helper Functions ---

def generate_keys():
    """Generates a new Ed25519 signing key and verify key."""
    signing_key = nacl.signing.SigningKey.generate()
    return signing_key, signing_key.verify_key

def create_capability_token(signing_key: nacl.signing.SigningKey, capabilities: List[str], expires_in_days: int = 30) -> str:
    """Creates and signs a capability token, returning it as a JSON string."""
    public_key_hex = signing_key.verify_key.encode(encoder=nacl.encoding.HexEncoder).decode('utf-8')
    token = CapabilityToken(
        granted_capabilities=capabilities,
        expiry=datetime.now(timezone.utc) + timedelta(days=expires_in_days),
        public_key=public_key_hex,
        signature=None, # Signature is added after serialization of the content
    )
    signed_message = signing_key.sign(token.to_signed_message())
    token.signature = signed_message.signature.hex()
    return token.model_dump_json()

def create_artifact(name: str, content: str, dependencies: list) -> Artifact:
    """Creates a sample artifact with a calculated digest and SBOM."""
    content_bytes = content.encode('utf-8')
    return Artifact(
        name=name,
        content=content_bytes,
        digest=hashlib.sha256(content_bytes).hexdigest(),
        sbom=[SBOMDependency(**dep) for dep in dependencies]
    )

def sign_artifacts(signing_key: nacl.signing.SigningKey, artifacts: list[Artifact]) -> dict:
    """Signs a list of artifacts and returns a dictionary of their signatures."""
    return {
        artifact.name: signing_key.sign(artifact.content).signature.hex()
        for artifact in artifacts
    }

async def run_scenario(framework: QuantumCryptographicSecurityFramework, operation: SystemOperation, test_name: str):
    """Runs a single verification scenario and prints a summary of the result."""
    print(f"\n--- Running Test Scenario: {test_name} ---")
    result = await framework.secure_complete_system_operation(operation)

    if result.operation_security_approved:
        print(f"✅ PASSED: {test_name}")
    else:
        print(f"❌ FAILED: {test_name}")
        if not result.capability_verification.verified:
            print(f"  -> Capability Failure: {result.capability_verification.reason}")
        if not result.supply_chain_verification.verified:
            print(f"  -> Supply Chain Failure: {result.supply_chain_verification.reason}")
        if not result.mathematical_security_verification.verified:
            print(f"  -> Mathematical Security Failure: {result.mathematical_security_verification.reason}")

    print(f"Comprehensive Certificate: {result.comprehensive_security_certificate}")
    print("-" * (len(test_name) + 25))


async def main():
    """Main function to run the security framework demonstration."""
    print("--- Quantum Cryptographic Security Framework Demonstration ---")

    # 1. Setup: Framework and cryptographic keys
    framework = QuantumCryptographicSecurityFramework()
    signing_key, _ = generate_keys()

    # 2. Define common components for the scenarios
    artifacts = [
        create_artifact("service_a.py", "print('service A')", [{"name": "requests", "version": "2.28.1", "license": "Apache-2.0"}]),
        create_artifact("service_b.py", "print('service B')", [{"name": "numpy", "version": "1.23.4", "license": "BSD-3-Clause"}]),
    ]

    sbom_reqs = SBOMRequirement(
        allowed_licenses=["Apache-2.0", "BSD-3-Clause", "MIT"],
        blocked_packages=["malicious-package"]
    )

    # --- Scenario 1: Successful Verification ---
    success_token = create_capability_token(signing_key, ["deploy_service", "access_database"])
    success_op = SystemOperation(
        operation_name="DeployProductionServices",
        required_capabilities=["deploy_service"],
        capability_tokens=[success_token],
        mathematical_security_constraints=[], # No extra constraints for the success case
        artifacts=artifacts,
        sbom_requirements=sbom_reqs,
        artifact_signatures=sign_artifacts(signing_key, artifacts)
    )
    await run_scenario(framework, success_op, "Successful Verification")

    # --- Scenario 2: Expired Capability Token ---
    expired_token = create_capability_token(signing_key, ["deploy_service"], expires_in_days=-1)
    expired_op = success_op.model_copy(update={"capability_tokens": [expired_token]})
    await run_scenario(framework, expired_op, "Expired Capability Token")

    # --- Scenario 3: Invalid Artifact Signature ---
    other_signing_key, _ = generate_keys()
    bad_signatures = sign_artifacts(other_signing_key, artifacts)
    bad_sig_op = success_op.model_copy(update={"artifact_signatures": bad_signatures})
    await run_scenario(framework, bad_sig_op, "Invalid Artifact Signature")

    # --- Scenario 4: Missing Capability ---
    limited_token = create_capability_token(signing_key, ["access_database"]) # Does not grant 'deploy_service'
    missing_cap_op = success_op.model_copy(update={"capability_tokens": [limited_token]})
    await run_scenario(framework, missing_cap_op, "Missing Capability")

    # --- Scenario 5: Blocked SBOM Dependency ---
    bad_artifact = create_artifact("bad_service.py", "print('bad stuff')", [{"name": "malicious-package", "version": "1.0", "license": "Unknown"}])
    bad_sbom_artifacts = artifacts + [bad_artifact]
    bad_sbom_op = success_op.model_copy(
        update={
            "artifacts": bad_sbom_artifacts,
            "artifact_signatures": sign_artifacts(signing_key, bad_sbom_artifacts)
        }
    )
    await run_scenario(framework, bad_sbom_op, "Blocked SBOM Dependency")

    # --- Scenario 6: Contradictory Mathematical Constraint ---
    # This test is designed to fail the mathematical verification. The constraint "(not deploy_service)"
    # contradicts the granted capability "deploy_service". This failure is caught early by the
    # CapabilityBasedSecurityEngine, demonstrating a defense-in-depth approach.
    math_fail_op = success_op.model_copy(
        update={
            "mathematical_security_constraints": ["(not deploy_service)"]
        }
    )
    await run_scenario(framework, math_fail_op, "Contradictory Mathematical Constraint")


if __name__ == "__main__":
    asyncio.run(main())
