import logging
import re
import json
from typing import Any, Dict, Optional
from dataclasses import dataclass

import jsonschema

from .client import QuantumState

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    safe: bool
    reason: Optional[str] = None
    risk_level: Optional[str] = None


class ResponseValidator:
    """
    A framework for validating LLM responses for safety, quality, and other constraints.
    """

    def __init__(self, safety_level: int = 4, quality_threshold: float = 0.5):
        self.safety_level = safety_level
        self.quality_threshold = quality_threshold

    def validate(
        self,
        response: Any,
        quantum_context: Optional[QuantumState] = None,
    ) -> bool:
        """
        Runs a series of validation checks on the LLM's response.
        """
        if not self._is_safe(response):
            logger.warning("Response failed safety check.")
            return False

        if not self._meets_quality(response):
            logger.warning("Response failed quality check.")
            return False

        if quantum_context and not self._check_quantum_constraints(response, quantum_context):
            logger.warning("Response failed quantum constraint check.")
            return False

        return True

    def _is_safe(self, response: Any) -> bool:
        """
        Checks the response against safety filters.
        This is a basic placeholder. A real implementation would use a content safety API
        or a more sophisticated model to detect harmful content.
        """
        if isinstance(response, str):
            content_to_check = response
        elif isinstance(response, dict) and "choices" in response:
            try:
                content_to_check = response["choices"][0]["message"]["content"]
            except (KeyError, IndexError):
                content_to_check = str(response)
        else:
            content_to_check = str(response)

        # Basic check for harmful patterns (very simplistic)
        harmful_keywords = ["illegal", "unethical", "harmful"]
        if any(keyword in content_to_check.lower() for keyword in harmful_keywords):
            return False

        return True

    def _meets_quality(self, response: Any) -> bool:
        """
        Assesses the quality of the response.
        This is a placeholder. A real system might check for grammar, coherence, or relevance.
        """
        # For now, we'll just check that the response is not empty.
        if isinstance(response, str):
            return len(response.strip()) > 0
        return True

    def _check_quantum_constraints(self, response: Any, quantum_context: QuantumState) -> bool:
        """
        Checks if the response adheres to any quantum-specific constraints.
        This is a placeholder for a complex validation logic that depends on the quantum state.
        """
        logger.info("Performing quantum constraint check on the response.")
        if not quantum_context.is_coherent():
            logger.warning("Quantum state is not coherent. Response may be unreliable.")
            # Depending on the system's needs, we might want to fail here
            # For now, we'll just log a warning.

        if isinstance(response, str):
            content_to_check = response
        elif isinstance(response, dict) and "choices" in response:
            content_to_check = response["choices"][0]["message"]["content"]
        else:
            content_to_check = str(response)

        # Example constraint: If system urgency is high, the response should be concise.
        if quantum_context.system_urgency > 0.8 and len(content_to_check) > 500:
            logger.warning("Response is too long for a high-urgency quantum state.")
            return False

        return True


class PromptSafetyValidator:
    """Validates LLM inputs and outputs for safety"""

    def __init__(self):
        self.injection_patterns = [
            r"ignore\s+previous\s+instructions",
            r"forget\s+everything\s+above",
            r"system\s*:\s*you\s+are\s+now",
            r"jailbreak\s+mode",
            r"developer\s+mode"
        ]

    def validate_input(self, prompt: str, context: Optional[str] = "") -> ValidationResult:
        """Validate input prompt for injection attempts"""
        # Check for injection patterns
        for pattern in self.injection_patterns:
            if re.search(pattern, prompt.lower()):
                return ValidationResult(
                    safe=False,
                    reason=f"Potential injection pattern detected: {pattern}",
                    risk_level="HIGH"
                )

        # Check prompt length limits
        if len(prompt) > 50000:  # Conservative limit
            return ValidationResult(
                safe=False,
                reason="Prompt exceeds maximum length",
                risk_level="MEDIUM"
            )

        # Validate context separation
        if context and "```" in prompt and "```" in context:
            # Ensure no context bleeding
            context_markers = prompt.count("```")
            if context_markers % 2 != 0:
                return ValidationResult(
                    safe=False,
                    reason="Unclosed code blocks may allow context confusion",
                    risk_level="MEDIUM"
                )

        return ValidationResult(safe=True)

    def validate_output(self, llm_output: str, expected_schema: Optional[Dict] = None) -> ValidationResult:
        """Validate LLM output against schema and safety constraints"""
        # JSON schema validation if provided
        if expected_schema:
            try:
                parsed = json.loads(llm_output)
                jsonschema.validate(instance=parsed, schema=expected_schema)
            except (json.JSONDecodeError, jsonschema.ValidationError) as e:
                return ValidationResult(
                    safe=False,
                    reason=f"Schema validation failed: {str(e)}",
                    risk_level="HIGH"
                )

        # Check for data exfiltration attempts
        sensitive_patterns = [
            r"api[_-]?key",
            r"password",
            r"secret",
            r"token",
            r"credential"
        ]

        for pattern in sensitive_patterns:
            if re.search(pattern, llm_output.lower()):
                return ValidationResult(
                    safe=False,
                    reason=f"Potential sensitive data exposure: {pattern}",
                    risk_level="HIGH"
                )

        return ValidationResult(safe=True)
