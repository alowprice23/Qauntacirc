import logging
import json
from typing import Any, Optional

from core.sbom_generator import SBOMGenerator
from monitoring.cve_monitor import CVEMonitor
from deployment.attestation import AttestationManager
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives import serialization

class SupplyChainValidator:
    """
    Orchestrates the supply chain security validation process.
    """

    def __init__(self, private_key: Optional[RSAPrivateKey] = None, private_key_path: Optional[str] = None):
        """
        Initializes the validator with the necessary components.
        A private key is only needed if you intend to generate attestations.
        """
        self.sbom_generator = SBOMGenerator()
        self.cve_monitor = CVEMonitor()
        self.attestation_manager = AttestationManager(private_key=private_key, private_key_path=private_key_path)

    def validate_project_dependencies(self, project_root: str, risk_budget: float) -> bool:
        """
        Runs a dependency scan on a project and assesses the risk.
        This is useful for pre-commit checks or CI pipelines.
        """
        logging.info(f"Starting supply chain dependency validation for project at '{project_root}'...")

        # 1. Generate SBOM
        logging.info("Generating Software Bill of Materials (SBOM)...")
        sbom = self.sbom_generator.generate_sbom(project_root)
        if not sbom.get("packages"):
            logging.warning("SBOM contained no packages. Vulnerability scan will be skipped.")
            return True

        logging.info(f"SBOM generated with {len(sbom['packages'])} packages.")

        # 2. Scan for CVEs
        logging.info("Scanning dependencies for known vulnerabilities (CVEs)...")
        vulnerabilities = self.cve_monitor.scan_dependencies(sbom)
        if not vulnerabilities:
            logging.info("No vulnerabilities found. The project is clean.")
            return True

        logging.warning(f"Found potential vulnerabilities in {len(vulnerabilities)} packages.")

        # 3. Assess risk budget impact
        logging.info("Assessing impact on risk budget...")
        risk_assessment = self.cve_monitor.assess_risk_budget_impact(vulnerabilities, risk_budget)

        vulnerability_counts = {
            "critical": risk_assessment.get('critical_vulnerabilities', 0),
            "high": risk_assessment.get('high_vulnerabilities', 0),
            "medium": risk_assessment.get('medium_vulnerabilities', 0),
            "low": risk_assessment.get('low_vulnerabilities', 0),
        }
        print("\n--- Vulnerability Risk Assessment Report ---")
        print(f"  Vulnerability Counts: {vulnerability_counts}")
        print(f"  Total Risk Increase: {risk_assessment.get('total_risk_increase', 0.0):.6f} (Budget: {risk_budget})")
        print(f"  Recommendation: {risk_assessment.get('recommendation', 'N/A')}")
        print("------------------------------------------\n")

        if not risk_assessment.get("within_budget", True) or risk_assessment.get('critical_vulnerabilities', 0) > 0:
            logging.error("Project validation failed due to high-risk vulnerabilities or exceeding risk budget.")
            return False

        logging.info("Project dependency validation passed.")
        return True

    def verify_artifact_attestation(self, signed_attestation_path: str, artifact_path: str) -> bool:
        """
        Verifies a build artifact against its signed attestation.
        This is critical for ensuring the integrity of artifacts in a deployment pipeline.
        """
        logging.info(f"Verifying artifact '{artifact_path}' using attestation '{signed_attestation_path}'...")

        try:
            with open(signed_attestation_path, 'r') as f:
                signed_attestation = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Failed to read or parse the attestation file: {e}")
            return False

        public_key_pem = signed_attestation.get("public_key")
        if not public_key_pem:
            logging.error("Verification failed: No public key found in the attestation.")
            return False

        try:
            public_key = serialization.load_pem_public_key(public_key_pem.encode())
        except ValueError as e:
            logging.error(f"Failed to load public key from attestation: {e}")
            return False

        verifier = self.attestation_manager

        expected_artifact_hash = verifier._compute_file_hash(artifact_path)

        is_valid = verifier.verify_attestation(
            signed_attestation=signed_attestation,
            expected_artifact_hash=expected_artifact_hash,
            public_key=public_key
        )

        if is_valid:
            logging.info("SUCCESS: Artifact attestation is valid and matches the artifact.")
        else:
            logging.error("FAILURE: Artifact attestation verification failed.")

        return is_valid
