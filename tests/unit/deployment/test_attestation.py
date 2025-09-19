import os
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from deployment.attestation import AttestationManager

@pytest.fixture
def key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private_key, private_key.public_key()

@pytest.fixture
def attestation_manager(key_pair):
    private_key, _ = key_pair
    return AttestationManager(private_key=private_key)

@pytest.fixture
def dummy_artifact(tmpdir):
    artifact_file = tmpdir.join("artifact.txt")
    artifact_file.write("This is a test artifact.")
    return str(artifact_file)

def test_generate_and_verify_attestation(attestation_manager, dummy_artifact):
    # Generate attestation
    build_metadata = {"build_id": "123"}
    signed_attestation = attestation_manager.generate_attestation(
        artifact_path=dummy_artifact,
        build_metadata=build_metadata
    )

    # Verify attestation
    artifact_hash = attestation_manager._compute_file_hash(dummy_artifact)
    is_valid = attestation_manager.verify_attestation(
        signed_attestation=signed_attestation,
        expected_artifact_hash=artifact_hash
    )

    assert is_valid

def test_collect_build_materials(attestation_manager, tmpdir):
    # Create a dummy source directory
    source_dir = tmpdir.mkdir("source")
    source_dir.join("file1.txt").write("content1")
    source_dir.mkdir("subdir").join("file2.txt").write("content2")

    materials = attestation_manager._collect_build_materials(str(source_dir))

    assert len(materials) == 2

    uris = {m['uri'] for m in materials}
    assert f"file://{os.path.abspath(os.path.join(str(source_dir), 'file1.txt'))}" in uris
    assert f"file://{os.path.abspath(os.path.join(str(source_dir), 'subdir', 'file2.txt'))}" in uris

    for material in materials:
        assert "sha256" in material["digest"]

def test_verify_fails_with_wrong_hash(attestation_manager, dummy_artifact):
    # Generate attestation
    build_metadata = {"build_id": "123"}
    signed_attestation = attestation_manager.generate_attestation(
        artifact_path=dummy_artifact,
        build_metadata=build_metadata
    )

    # Verify with wrong hash
    is_valid = attestation_manager.verify_attestation(
        signed_attestation=signed_attestation,
        expected_artifact_hash="a_clearly_incorrect_hash_value"
    )

    assert not is_valid

def test_verify_fails_with_tampered_attestation(attestation_manager, dummy_artifact):
    # Generate attestation
    build_metadata = {"build_id": "123"}
    signed_attestation = attestation_manager.generate_attestation(
        artifact_path=dummy_artifact,
        build_metadata=build_metadata
    )

    # Tamper with the attestation payload
    signed_attestation["attestation"]["build_metadata"]["build_id"] = "456"

    # Verify tampered attestation
    artifact_hash = attestation_manager._compute_file_hash(dummy_artifact)
    is_valid = attestation_manager.verify_attestation(
        signed_attestation=signed_attestation,
        expected_artifact_hash=artifact_hash
    )

    assert not is_valid

def test_init_without_key_and_verify(key_pair, dummy_artifact):
    # This tests the scenario where the verifier doesn't have the private key.
    private_key, public_key = key_pair
    signing_manager = AttestationManager(private_key=private_key)

    # Generate attestation
    signed_attestation = signing_manager.generate_attestation(dummy_artifact, {})

    # Verifier initialized without a private key
    verifier_manager = AttestationManager()
    artifact_hash = verifier_manager._compute_file_hash(dummy_artifact)

    is_valid = verifier_manager.verify_attestation(
        signed_attestation=signed_attestation,
        expected_artifact_hash=artifact_hash,
        public_key=public_key
    )

    assert is_valid
