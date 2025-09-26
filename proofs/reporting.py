from typing import Dict, Any, List
import json

class VerificationReporter:
    """
    Generates reports from verification results.
    """
    def __init__(self, verification_results: Dict[str, Any], obligation_file: str):
        self.results = verification_results
        self.obligation_file = obligation_file
        with open(obligation_file, 'r') as f:
            self.obligations_data = json.load(f)

    def generate_report(self, report_format: str = 'text') -> str:
        """
        Generates a verification report in the specified format.
        """
        if report_format == 'text':
            return self._generate_text_report()
        elif report_format == 'json':
            return json.dumps(self.obligations_data, indent=2)
        else:
            raise ValueError(f"Unsupported report format: {report_format}")

    def _generate_text_report(self) -> str:
        """
        Generates a human-readable text report.
        """
        obligations = self.obligations_data.get("obligations", [])
        total_obligations = len(obligations)
        if total_obligations == 0:
            return "No proof obligations found."

        proved_count = sum(1 for ob in obligations if ob.get("status") == "proved")
        failed_count = sum(1 for ob in obligations if ob.get("status") == "failed")
        pending_count = total_obligations - proved_count - failed_count

        coverage = (proved_count / total_obligations) * 100 if total_obligations > 0 else 0

        # Calculate confidence score (simple version)
        confidence_score = self._calculate_confidence(obligations)

        report_lines = [
            "========================================",
            "   Verification Status Report         ",
            "========================================",
            f"Obligation File: {self.obligation_file}",
            f"Overall Status: {self.results.get('overall_status', 'unknown').upper()}",
            "---",
            "Summary:",
            f"  - Total Obligations: {total_obligations}",
            f"  - Proved:            {proved_count}",
            f"  - Failed:            {failed_count}",
            f"  - Pending/Skipped:   {pending_count}",
            "---",
            f"Proof Coverage: {coverage:.2f}%",
            f"Verification Confidence: {confidence_score:.2f}/100.00",
            "========================================",
            "Detailed Breakdown:",
        ]

        for ob in obligations:
            report_lines.append(f"\n[ ] Obligation: {ob['id']}")
            report_lines.append(f"    - Description: {ob['description']}")
            report_lines.append(f"    - Type:        {ob.get('type', 'N/A')}")
            report_lines.append(f"    - Status:      {ob.get('status', 'pending').upper()}")
            if ob.get("status") == "failed":
                report_lines.append(f"    - Reason:      {ob.get('reason', 'No details provided.')}")
            if ob.get("status") == "proved":
                report_lines.append(f"    - Engine:      {ob.get('engine', 'N/A')}")

        return "\n".join(report_lines)

    def _calculate_confidence(self, obligations: List[Dict[str, Any]]) -> float:
        """
        Calculates a confidence score based on the verification methods used.
        Coq provides the highest confidence, followed by SMT, then property tests.
        """
        if not obligations:
            return 0.0

        engine_weights = {
            "coq": 1.0,
            "smt": 0.8,
            "property_based": 0.6,
            "default": 0.5 # For other or unknown engines
        }
        max_score = sum(engine_weights.get(ob.get("type"), engine_weights["default"]) for ob in obligations)
        achieved_score = sum(
            engine_weights.get(ob.get("engine"), 0) for ob in obligations if ob.get("status") == "proved"
        )

        return (achieved_score / max_score) * 100 if max_score > 0 else 0

# Example Usage:
if __name__ == '__main__':
    # Create dummy files for testing
    dummy_results = {
        "overall_status": "failed",
        "details": [
            {"obligation-1": {"status": "failed", "reason": "Property could not be proved."}},
            {"obligation-2": {"status": "pending", "reason": "Coq verification not implemented."}},
        ]
    }
    dummy_obligations = {
        "version": "1.0", "task_id": "task-123", "file": "task-123.py",
        "obligations": [
            {"id": "obligation-1", "type": "smt", "property": "no integer overflow", "description": "Desc 1", "status": "failed", "reason": "Property could not be proved."},
            {"id": "obligation-2", "type": "coq", "property": "correctness", "description": "Desc 2", "status": "pending", "reason": "Coq not implemented."},
            {"id": "obligation-3", "type": "smt", "property": "x > 5", "description": "Desc 3", "status": "proved", "engine": "smt"}
        ]
    }
    with open("dummy_obligations.json", 'w') as f:
        json.dump(dummy_obligations, f)

    reporter = VerificationReporter(dummy_results, "dummy_obligations.json")
    text_report = reporter.generate_report('text')
    print(text_report)

    import os
    os.remove("dummy_obligations.json")