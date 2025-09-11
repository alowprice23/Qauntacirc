"""
Prompt Security Module

This module provides tools for detecting and preventing prompt injection attacks.

MATHEMATICAL FOUNDATION:
=======================
Prompt security is modeled as a classification problem:
- Given a prompt P, classify it as either "safe" or "injected".
- Let S be the space of safe prompts and I be the space of injected prompts.
- The goal is to find a function f: P -> {S, I} that minimizes misclassification.
- f is composed of multiple checks: f(p) = f_1(p) OR f_2(p) OR ... OR f_n(p)

PHYSICS PRINCIPLE:
=================
Prompt security is analogous to a firewall in information flow:
- The firewall inspects incoming data (prompts) for malicious content.
- It blocks information that violates security policies (injection patterns).
- The goal is to maintain the integrity of the system's information state.
"""

import re
import yaml
from typing import List, Dict, Any, Optional

class InjectionDetector:
    """
    Detects potential prompt injection attacks in user-provided content.
    """
    def __init__(self, pattern_file: Optional[str] = None):
        """
        Initializes the detector with a list of regex patterns.

        Args:
            pattern_file: Path to a YAML file containing injection patterns.
                          If None, a default set of patterns is used.
        """
        if pattern_file:
            with open(pattern_file, 'r') as f:
                self.patterns = yaml.safe_load(f).get("injection_patterns", [])
        else:
            self.patterns = [
                # Common instruction hijacking
                r"ignore previous instructions",
                r"ignore the above and",
                r"forget the above",
                r"do something else",
                r"stop being an ai",
                r"you are now a character named",

                # Role-playing and persona hijacking
                r"act as",
                r"behave as",
                r"you are a new type of ai",

                # Command injection style
                r"---",
                r"===",
                r"\n\n",

                # Evasion techniques
                r"in json format",
                r"in markdown format",
                r"in base64",
            ]

        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.patterns]

    def detect(self, prompt: str) -> bool:
        """
        Detects if a prompt contains any of the injection patterns.

        Args:
            prompt: The user-provided prompt string.

        Returns:
            True if an injection pattern is detected, False otherwise.
        """
        for pattern in self.compiled_patterns:
            if pattern.search(prompt):
                return True
        return False

    def sanitize(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Sanitizes a list of messages, checking for injections in user content.

        Args:
            messages: A list of message dictionaries.

        Returns:
            The sanitized list of messages.

        Raises:
            ValueError: If a prompt injection is detected in user content.
        """
        for message in messages:
            if message.get("role") == "user":
                if self.detect(message.get("content", "")):
                    raise ValueError("Prompt injection detected in user content.")
        return messages
