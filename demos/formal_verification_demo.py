import asyncio
import pprint

from formal_verification.data_structures import (
    SystemSpecification,
    SystemProperty,
    PropertyType,
)
from formal_verification.framework import MultiLogicVerificationFramework


def create_sample_system():
    """Creates a sample system specification for demonstration."""
    properties = [
        # Functional Properties (for Coq)
        SystemProperty(id="FP001", description="Correctness of sorting algorithm", property_type=PropertyType.FUNCTIONAL, specification={"tactic": "induction"}),
        SystemProperty(id="FP002", description="State machine transition validity", property_type=PropertyType.FUNCTIONAL, specification={"tactic": "cases"}),

        # Arithmetic Properties (for SMT)
        SystemProperty(id="AP001", description="Absence of buffer overflows", property_type=PropertyType.ARITHMETIC, specification={"expression": "index < max_size"}),
        SystemProperty(id="AP002", description="Non-negativity of account balance", property_type=PropertyType.ARITHMETIC, specification={"expression": "balance >= 0"}),
        SystemProperty(id="AP003", description="Array bounds check", property_type=PropertyType.ARITHMETIC, specification={"expression": "forall i. 0 <= i < len(a) -> a[i] > 0"}),

        # Temporal Properties (for UPPAAL)
        SystemProperty(id="TP001", description="Liveness: Request eventually granted", property_type=PropertyType.TEMPORAL, specification={"formula": "A<> Grant"}),
        SystemProperty(id="TP002", description="Safety: Mutex is exclusive", property_type=PropertyType.TEMPORAL, specification={"formula": "A[] not (crit1 and crit2)"}),

        # Probabilistic Properties (for PRISM)
        SystemProperty(id="PP001", description="Probability of reaching success state > 0.99", property_type=PropertyType.PROBABILISTIC, specification={"pctl": 'P>=0.99 [ F "success" ]'}),
        SystemProperty(id="PP002", description="Expected number of failures < 5", property_type=PropertyType.PROBABILISTIC, specification={"csl": 'R{"failures"}<=5 [ F "terminate" ]'}),
    ]
    return SystemSpecification(
        name="Autonomous Drone Control System",
        version="1.2.0",
        properties=properties,
    )

async def main():
    """Main function to run the demonstration."""
    system_to_verify = create_sample_system()
    framework = MultiLogicVerificationFramework()

    # This is a placeholder for the actual call, which needs to be run in a context
    # that has the `formal_verification` package in its path.
    # In a real scenario, you would run this script as a module.
    # For the purpose of this demonstration, we are just creating the file.
    print("Demonstration script created. To run it, execute `python -m demos.formal_verification_demo` from the root directory.")


if __name__ == "__main__":
    # The following code will be executed when the script is run directly
    async def run_verification():
        system_to_verify = create_sample_system()
        framework = MultiLogicVerificationFramework()

        result = await framework.verify_system_with_multi_logic_guarantees(system_to_verify)

        print("\n\n--- MULTI-LOGIC VERIFICATION REPORT ---")
        print("=" * 40)

        print(f"\n[*] System: {result.verification_certificate.system_name} v{result.verification_certificate.system_version}")
        print(f"[*] Verification Status: {'PASSED' if result.meets_coverage_threshold else 'FAILED'}")
        print(f"[*] Coverage Threshold (>= 85%): {'Met' if result.meets_coverage_threshold else 'Not Met'}")

        print("\n--- Coverage Analysis ---")
        print(f"  - Formal Coverage: {result.formal_coverage_percentage}%")
        print(f"  - Total Estimated Coverage: {result.total_coverage_percentage}%")

        all_results = result.coq_results + result.smt_results + result.uppaal_results + result.prism_results
        failed_results = [r for r in all_results if not r.verified]

        if not failed_results:
            print("  - All properties successfully verified.")
        else:
            print("  - Uncovered/Failed Properties:")
            for res in failed_results:
                print(f"    - {res.property_id}: {res.error_message}")

        print("\n--- Detailed Verification Results ---")
        composed_details = result.composed_result.details
        pprint.pprint(composed_details)

        print("\n--- Rely-Guarantee Composition ---")
        pprint.pprint(result.composed_result.rely_guarantee_assumptions)

        print("\n--- Verification Certificate ---")
        # Use dataclasses.asdict for cleaner printing if available, otherwise pprint
        try:
            from dataclasses import asdict
            pprint.pprint(asdict(result.verification_certificate))
        except ImportError:
            pprint.pprint(result.verification_certificate)

        print("=" * 40)

    # Add the project root to the path to allow imports
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    from formal_verification.framework import MultiLogicVerificationFramework
    from formal_verification.data_structures import SystemSpecification, SystemProperty, PropertyType

    asyncio.run(run_verification())
