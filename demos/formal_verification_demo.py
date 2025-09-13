import asyncio
import os
import pprint
import sys
from dataclasses import asdict

# Add the project root to the path to allow imports, assuming the script is run from the root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from formal_verification.data_structures import (
    SystemSpecification,
    SystemProperty,
    PropertyType,
)
from formal_verification.framework import MultiLogicVerificationFramework


def create_sample_system() -> SystemSpecification:
    """
    Creates a sample system specification for the demonstration.
    This system represents a simplified drone controller with various properties
    that need to be formally verified.
    """
    properties = [
        # --- Functional Properties (for Coq) ---
        # Verified: A correct property for our deterministic mock
        SystemProperty(id="FP001", description="Correctness of state transition logic", property_type=PropertyType.FUNCTIONAL, specification={"tactic": "induction"}),
        # Unverified: An incorrect property for our deterministic mock
        SystemProperty(id="FP002", description="Idempotency of landing command", property_type=PropertyType.FUNCTIONAL, specification={"tactic": "cases"}),

        # --- Arithmetic Properties (for Z3 SMT Solver) ---
        # Verified: A simple tautology
        SystemProperty(id="AP001", description="Altitude sensor consistency", property_type=PropertyType.ARITHMETIC, specification={"expression": "alt_1 > 0 or alt_1 <= 0"}),
        # Unverified: A falsifiable statement to demonstrate counter-example
        SystemProperty(id="AP002", description="Rotor speed safety margin", property_type=PropertyType.ARITHMETIC, specification={"expression": "speed_1 < 5000 and speed_1 > 5100"}),
        # Verified: A valid bounds check
        SystemProperty(id="AP003", description="Geofence boundary check", property_type=PropertyType.ARITHMETIC, specification={"expression": "x_pos < 1000 and y_pos < 1000"}),

        # --- Temporal Properties (for UPPAAL) ---
        # Verified: A liveness property our mock will pass
        SystemProperty(id="TP001", description="Liveness: Connection to base is eventually established", property_type=PropertyType.TEMPORAL, specification={"formula": "A<> ConnectionEstablished"}),
        # Unverified: A safety property our mock will fail
        SystemProperty(id="TP002", description="Safety: Drone never enters no-fly zone", property_type=PropertyType.TEMPORAL, specification={"formula": "A[] not NoFlyZone"}),

        # --- Probabilistic Properties (for PRISM) ---
        # Verified: A high-probability event our mock will pass
        SystemProperty(id="PP001", description="Probability of successful packet transmission > 0.99", property_type=PropertyType.PROBABILISTIC, specification={"pctl": 'P>=0.99 [ F "packet_acked" ]'}),
        # Unverified: A low-probability event our mock will fail
        SystemProperty(id="PP002", description="Probability of hardware failure < 0.001", property_type=PropertyType.PROBABILISTIC, specification={"pctl": 'P<0.001 [ G "no_hardware_failure" ]'}),
    ]
    return SystemSpecification(
        name="Autonomous Drone Control System",
        version="1.2.0",
        properties=properties,
    )


async def main():
    """Main function to run the formal verification demonstration."""
    system_to_verify = create_sample_system()
    framework = MultiLogicVerificationFramework()

    result = await framework.verify_system_with_multi_logic_guarantees(system_to_verify)

    print("\n\n--- MULTI-LOGIC VERIFICATION REPORT ---")
    print("=" * 40)

    cert = result.verification_certificate
    print(f"\n[*] System: {cert.system_name} v{cert.system_version}")
    print(f"[*] Verification Status: {'PASSED' if result.meets_coverage_threshold else 'FAILED'}")
    print(f"[*] Coverage Threshold (>= 85%): {'Met' if result.meets_coverage_threshold else 'Not Met'}")

    print("\n--- Coverage Analysis ---")
    print(f"  - Formal Coverage: {result.formal_coverage_percentage}%")
    print(f"  - Total Estimated Coverage: {result.total_coverage_percentage}%")

    if not result.composed_result.all_properties_verified:
        print("  - Uncovered/Failed Properties:")
        all_results = result.coq_results + result.smt_results + result.uppaal_results + result.prism_results
        for res in all_results:
            if not res.verified:
                print(f"    - {res.property_id}: {res.error_message}")
    else:
        print("  - All properties successfully verified.")


    print("\n--- Detailed Verification Results ---")
    pprint.pprint(result.composed_result.details)

    print("\n--- Rely-Guarantee Composition Assumptions ---")
    pprint.pprint(result.composed_result.rely_guarantee_assumptions)

    print("\n--- Verification Certificate ---")
    pprint.pprint(asdict(cert))

    print("=" * 40)


if __name__ == "__main__":
    asyncio.run(main())
