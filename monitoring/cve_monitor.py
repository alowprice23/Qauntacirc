import httpx
import json
import logging
from typing import Dict, List, Any, Optional

class CVEMonitor:
    """Monitors dependencies for known vulnerabilities"""

    def __init__(self, client: Optional[httpx.Client] = None):
        self.cve_databases = {
            "osv": "https://api.osv.dev/v1/query",
            "nvd": "https://services.nvd.nist.gov/rest/json/cves/2.0",
        }
        self.cache = {}
        self.client = client if client else httpx.Client()

    def scan_dependencies(self, sbom: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Scan SBOM components for known vulnerabilities"""
        vulnerabilities = {}

        for package in sbom.get("packages", []):
            package_name = package.get("name")
            package_version = package.get("version")

            if not package_name or not package_version:
                continue

            # Check cache first
            cache_key = f"{package_name}@{package_version}"
            if cache_key in self.cache:
                if self.cache[cache_key]:
                    vulnerabilities[cache_key] = self.cache[cache_key]
                continue

            package_vulnerabilities = []

            # Check OSV database for Python packages
            if package.get("purl", "").startswith("pkg:pypi/"):
                osv_vulns = self._query_osv_database(package_name, package_version)
                package_vulnerabilities.extend(osv_vulns)

            # NVD database check is a placeholder, as it's more complex.
            # cpe = package.get("cpe")
            # nvd_vulns = self._query_nvd_database(package_name, cpe)
            # package_vulnerabilities.extend(nvd_vulns)

            # Cache results
            self.cache[cache_key] = package_vulnerabilities

            if package_vulnerabilities:
                vulnerabilities[cache_key] = package_vulnerabilities

        return vulnerabilities

    def _query_osv_database(self, package_name: str, package_version: str) -> List[Dict]:
        """Queries the OSV database for vulnerabilities."""
        query = {
            "version": package_version,
            "package": {
                "name": package_name,
                "ecosystem": "PyPI"
            }
        }
        try:
            response = self.client.post(self.cve_databases["osv"], json=query, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data.get("vulns", [])
        except (httpx.HTTPStatusError, json.JSONDecodeError, httpx.RequestError) as e:
            logging.error(f"Error querying OSV database for {package_name}@{package_version}: {e}")
            return []

    def _query_nvd_database(self, package_name: str, cpe: Optional[str] = None) -> List[Dict]:
        """Placeholder for querying NVD database."""
        return []

    def assess_risk_budget_impact(self,
                                 vulnerabilities: Dict[str, List[Dict]],
                                 risk_budget: float) -> Dict[str, Any]:
        """Assess impact of vulnerabilities on risk budget"""
        total_risk_increase = 0.0
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0

        all_vulns = []
        for package, vulns in vulnerabilities.items():
            all_vulns.extend(vulns)

        for vuln in all_vulns:
            severity_score = 0.0
            # OSV format includes a list of severities. We look for CVSS v3.
            for severity in vuln.get("severity", []):
                if severity.get("type") == "CVSS_V3":
                    try:
                        # The score is often in a vector string, e.g., "CVSS:3.1/AV:N/AC:L/..."
                        # A simpler format is just the base score as a number.
                        # This implementation is simplified and assumes a simple numeric score string.
                        severity_score = float(severity.get("score", "0.0"))
                    except (ValueError, TypeError):
                        pass # Keep severity_score 0 if score is not a valid float
                    break

            if severity_score >= 9.0:
                risk_increase = 0.001
                critical_count += 1
            elif severity_score >= 7.0:
                risk_increase = 0.0001
                high_count += 1
            elif severity_score >= 4.0:
                risk_increase = 0.00001
                medium_count += 1
            elif severity_score > 0:
                risk_increase = 0.000001
                low_count += 1

            total_risk_increase += risk_increase

        return {
            "total_risk_increase": total_risk_increase,
            "within_budget": total_risk_increase <= risk_budget,
            "critical_vulnerabilities": critical_count,
            "high_vulnerabilities": high_count,
            "medium_vulnerabilities": medium_count,
            "low_vulnerabilities": low_count,
            "recommendation": self._generate_risk_recommendation(
                total_risk_increase, risk_budget, critical_count, high_count
            )
        }

    def _generate_risk_recommendation(self, total_risk_increase: float, risk_budget: float, critical_count: int, high_count: int) -> str:
        """Generates a risk recommendation based on the assessment."""
        if total_risk_increase > risk_budget:
            return "Risk budget exceeded. Immediate remediation required."
        if critical_count > 0:
            return f"Action required: {critical_count} critical vulnerabilities found."
        if high_count > 0:
            return f"Action recommended: {high_count} high severity vulnerabilities found."
        return "Risk level is within acceptable limits."
