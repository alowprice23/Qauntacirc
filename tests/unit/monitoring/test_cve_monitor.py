import pytest
import httpx
from unittest.mock import MagicMock, create_autospec

from monitoring.cve_monitor import CVEMonitor

@pytest.fixture
def mock_httpx_client():
    mock_client = create_autospec(httpx.Client, instance=True)
    return mock_client

def test_scan_dependencies_with_vulnerabilities(mock_httpx_client):
    # Mock the response from the OSV API
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "vulns": [
            {"id": "CVE-2021-1234", "summary": "A vulnerability", "severity": [{"type": "CVSS_V3", "score": "9.8"}]}
        ]
    }
    mock_httpx_client.post.return_value = mock_response

    cve_monitor = CVEMonitor(client=mock_httpx_client)

    sbom = {
        "packages": [
            {"name": "vulnerable-package", "version": "1.0.0", "purl": "pkg:pypi/vulnerable-package"}
        ]
    }

    vulnerabilities = cve_monitor.scan_dependencies(sbom)

    assert "vulnerable-package@1.0.0" in vulnerabilities
    assert len(vulnerabilities["vulnerable-package@1.0.0"]) == 1
    assert vulnerabilities["vulnerable-package@1.0.0"][0]["id"] == "CVE-2021-1234"

def test_scan_dependencies_no_vulnerabilities(mock_httpx_client):
    # Mock an empty response
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {} # No vulns found
    mock_httpx_client.post.return_value = mock_response

    cve_monitor = CVEMonitor(client=mock_httpx_client)

    sbom = {
        "packages": [
            {"name": "clean-package", "version": "1.0.0", "purl": "pkg:pypi/clean-package"}
        ]
    }

    vulnerabilities = cve_monitor.scan_dependencies(sbom)

    assert not vulnerabilities

def test_risk_assessment(mock_httpx_client):
    cve_monitor = CVEMonitor(client=mock_httpx_client)

    vulnerabilities = {
        "critical-package@1.0.0": [{"severity": [{"type": "CVSS_V3", "score": "9.5"}]}],
        "high-package@1.0.0": [{"severity": [{"type": "CVSS_V3", "score": "8.0"}]}],
        "medium-package@1.0.0": [{"severity": [{"type": "CVSS_V3", "score": "6.0"}]}],
        "low-package@1.0.0": [{"severity": [{"type": "CVSS_V3", "score": "3.0"}]}]
    }

    risk_assessment = cve_monitor.assess_risk_budget_impact(vulnerabilities, risk_budget=0.001)

    assert risk_assessment["critical_vulnerabilities"] == 1
    assert risk_assessment["high_vulnerabilities"] == 1
    assert risk_assessment["medium_vulnerabilities"] == 1
    assert risk_assessment["low_vulnerabilities"] == 1
    assert not risk_assessment["within_budget"]

def test_risk_assessment_within_budget(mock_httpx_client):
    cve_monitor = CVEMonitor(client=mock_httpx_client)

    vulnerabilities = {
        "low-package@1.0.0": [{"severity": [{"type": "CVSS_V3", "score": "3.0"}]}]
    }

    risk_assessment = cve_monitor.assess_risk_budget_impact(vulnerabilities, risk_budget=0.01)

    assert risk_assessment["within_budget"]
    assert risk_assessment["recommendation"] == "Risk level is within acceptable limits."
