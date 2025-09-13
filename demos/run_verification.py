import asyncio
import uuid
from pprint import pprint

from formal_verification.data_structures import (
    SystemSpecification,
    SystemProperty,
    PropertyType,
)
from formal_verification.framework import MultiLogicVerificationFramework


def create_sample_system_specification() -> SystemSpecification:
    """Creates a sample system specification for demonstration purposes."""
    properties = [
        SystemProperty(
            id=str(uuid.uuid4()),
            description="Functional: User authentication logic is correct.",
            property_type=PropertyType.FUNCTIONAL,
            specification={"module": "auth", "function": "authenticate"},
        ),
        SystemProperty(
            id=str(uuid.uuid4()),
            description="Arithmetic: A satisfiable property (x > 10 and x < 20).",
            property_type=PropertyType.ARITHMETIC,
            specification={
                "variables": ["x"],
                "constraints": ["x > 10", "x < 20"],
            },
        ),
        SystemProperty(
            id=str(uuid.uuid4()),
            description="Arithmetic: An unsatisfiable property (y > 10 and y < 5).",
            property_type=PropertyType.ARITHMETIC,
            specification={
                "variables": ["y"],
                "constraints": ["y > 10", "y < 5"],
            },
        ),
        SystemProperty(
            id=str(uuid.uuid4()),
            description="Temporal: A request is always eventually followed by a response.",
            property_type=PropertyType.TEMPORAL,
            specification={"pattern": "eventually", "scope": "global"},
        ),
        SystemProperty(
            id=str(uuid.uuid4()),
            description="Probabilistic: System availability is >= 99.9%.",
            property_type=PropertyType.PROBABILISTIC,
            specification={"metric": "availability", "threshold": 0.999},
        ),
        SystemProperty(
            id=str(uuid.uuid4()),
            description="Functional: Data encryption meets FIPS 140-2 standards.",
            property_type=PropertyType.FUNCTIONAL,
            specification={"module": "crypto", "standard": "FIPS 140-2"},
        ),
    ]
    return SystemSpecification(
        name="QuantaCirc-DemoSystem",
        version="1.0.0",
        properties=properties,
    )


async def main():
    """Main function to run the verification demo."""
    print("--- Formal Verification Demo for QuantaCirc ---")

    # 1. Create a sample system specification
    system_spec = create_sample_system_specification()
    print("\n--- System Specification ---")
    pprint(system_spec)

    # 2. Initialize the verification framework
    framework = MultiLogicVerificationFramework()

    # 3. Run the verification process
    print("\n--- Running Verification ---")
    result = await framework.verify_system_with_multi_logic_guarantees(system_spec)

    # 4. Print the comprehensive results
    print("\n--- Comprehensive Verification Result ---")
    pprint(result)

    print("\n--- Verification Certificate ---")
    pprint(result.verification_certificate)

    print(f"\nMeets Coverage Threshold (>= 85%): {result.meets_coverage_threshold}")


if __name__ == "__main__":
    asyncio.run(main())
