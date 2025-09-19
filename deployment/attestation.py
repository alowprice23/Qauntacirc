import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


class AttestationManager:
    """Manages cryptographic attestations for build artifacts"""

    def __init__(self, private_key_path: Optional[str] = None, private_key: Optional[RSAPrivateKey] = None):
        if private_key:
            self.private_key = private_key
            self.public_key = self.private_key.public_key()
        elif private_key_path:
            with open(private_key_path, 'rb') as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None
                )
            self.public_key = self.private_key.public_key()
        else:
            self.private_key = None
            self.public_key = None

    def generate_attestation(self,
                           artifact_path: str,
                           build_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate signed attestation for build artifact"""
        if not self.private_key or not self.public_key:
            raise Exception("AttestationManager not initialized with a private key. Cannot generate attestation.")

        # Compute artifact hash
        artifact_hash = self._compute_file_hash(artifact_path)

        # Create attestation payload
        attestation = {
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "artifact": {
                "path": artifact_path,
                "sha256": artifact_hash,
                "size": os.path.getsize(artifact_path)
            },
            "build_metadata": build_metadata,
            "builder": {
                "id": "quantacirc-builder",
                "version": "1.0.0"
            },
            "materials": self._collect_build_materials(build_metadata.get("source_dir", ".")),
            "recipe": {
                "type": "shell",
                "defined_in_material": 0,
                "entry_point": build_metadata.get("build_command", "")
            }
        }

        # Sign attestation
        attestation_json = json.dumps(attestation, sort_keys=True)
        signature = self.private_key.sign(
            attestation_json.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return {
            "attestation": attestation,
            "signature": signature.hex(),
            "public_key": self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode()
        }

    def verify_attestation(self,
                          signed_attestation: Dict[str, Any],
                          expected_artifact_hash: str,
                          public_key: Optional[RSAPublicKey] = None) -> bool:
        """Verify signed attestation"""
        key_to_use = public_key if public_key else self.public_key
        if not key_to_use:
            raise ValueError("Verification requires a public key to be provided.")

        try:
            # Verify signature
            attestation_json = json.dumps(signed_attestation["attestation"], sort_keys=True)
            signature = bytes.fromhex(signed_attestation["signature"])

            key_to_use.verify(
                signature,
                attestation_json.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            # Verify artifact hash matches
            actual_hash = signed_attestation["attestation"]["artifact"]["sha256"]
            return actual_hash == expected_artifact_hash

        except Exception as e:
            logging.error(f"Attestation verification failed: {e}")
            return False

    def _compute_file_hash(self, file_path: str) -> str:
        """Computes the SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _collect_build_materials(self, source_dir: str) -> List[Dict[str, Any]]:
        """
        Scans the source directory and records the hashes of all files.
        This is a simplified implementation; a real one might ignore .gitignore'd files.
        """
        materials = []
        for root, _, files in os.walk(source_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    file_hash = self._compute_file_hash(file_path)
                    materials.append({
                        "uri": f"file://{os.path.abspath(file_path)}",
                        "digest": {"sha256": file_hash}
                    })
                except IOError:
                    # Ignore files that cannot be read
                    pass
        return materials
