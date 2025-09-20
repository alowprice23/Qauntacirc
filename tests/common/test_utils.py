import textwrap
from typing import List, Dict, Optional

class TestDiagnostic:
    """A helper class to provide detailed, structured feedback for failed tests."""

    def __init__(self,
                 component_name: str,
                 expected_behavior: str,
                 failure_indicators: List[str],
                 build_instructions: List[str],
                 mathematical_requirements: List[str],
                 acceptance_criteria: Dict[str, str],
                 physics_principle: str,
                 related_components: Optional[List[str]] = None):
        self.component_name = component_name
        self.expected_behavior = expected_behavior
        self.failure_indicators = failure_indicators
        self.build_instructions = build_instructions
        self.mathematical_requirements = mathematical_requirements
        self.acceptance_criteria = acceptance_criteria
        self.physics_principle = physics_principle
        self.related_components = related_components or []

    def format_failure_message(self, error_message: str) -> str:
        """Formats the detailed failure message for pytest.fail()."""

        header = f"QUANTACIRC TEST FAILURE: {self.component_name}"

        formatted_message = f"""
{('=' * len(header))}
{header}
{('=' * len(header))}

EXPECTED BEHAVIOR:
  {self.expected_behavior}

ACTUAL ERROR:
{textwrap.indent(error_message, '  ')}

FAILURE INDICATORS:
{self._format_list(self.failure_indicators, '❌')}

WHAT TO BUILD:
  The following components are missing or incomplete:
{self._format_list(self.build_instructions, '🔨')}

MATHEMATICAL REQUIREMENTS:
  These mathematical properties must be satisfied:
{self._format_list(self.mathematical_requirements, '📐')}

ACCEPTANCE CRITERIA:
  Tests will pass when these conditions are met:
{self._format_dict(self.acceptance_criteria, '✅')}

PHYSICS PRINCIPLE:
  {self.physics_principle}
"""
        if self.related_components:
            formatted_message += f"""
RELATED COMPONENTS:
  These components may also need attention:
{self._format_list(self.related_components, '🔗')}
"""

        formatted_message += f"\n{('=' * len(header))}"
        return formatted_message

    def _format_list(self, items: List[str], icon: str) -> str:
        return textwrap.indent('\n'.join(f"{icon} {item}" for item in items), '  ')

    def _format_dict(self, items: Dict[str, str], icon: str) -> str:
        return textwrap.indent('\n'.join(f"{icon} {key}: {value}" for key, value in items.items()), '  ')
