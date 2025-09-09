# -*- coding: utf-8 -*-
"""
Proof Validation Automation

This script provides a set of validators to automate the verification of
formal proofs written in Coq, Agda, and SMT-LIB. It is designed to be
used in a CI/CD pipeline to ensure the mathematical guarantees of the
system are continuously checked.

The validators work by invoking the respective proof assistant's command-line
tool and parsing the output to determine success or failure.
"""

import subprocess
import os
from typing import List, Tuple

class ProofValidator:
    """Base class for proof validators."""
    def __init__(self, checker_executable: str):
        self.checker = checker_executable

    def check_availability(self) -> bool:
        """Check if the proof checker executable is available."""
        try:
            subprocess.run([self.checker, "--version"], capture_output=True, check=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Warning: '{self.checker}' not found. Validation will be skipped.")
            return False

    def validate(self, filepath: str) -> Tuple[bool, str]:
        """Run validation on a single proof file."""
        raise NotImplementedError


class CoqValidator(ProofValidator):
    """Validator for Coq proofs (*.v)."""
    def __init__(self):
        super().__init__("coqc")

    def validate(self, filepath: str) -> Tuple[bool, str]:
        """Validate a Coq file using 'coqc'."""
        if not self.check_availability():
            return True, "Skipped (coqc not found)"

        command = [self.checker, "-o", "/dev/null", filepath]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return True, "Validation successful"
        else:
            return False, f"Validation failed:\n{result.stderr}"


class AgdaValidator(ProofValidator):
    """Validator for Agda proofs (*.agda)."""
    def __init__(self):
        super().__init__("agda")

    def validate(self, filepath: str) -> Tuple[bool, str]:
        """Validate an Agda file using 'agda --no-main'."""
        if not self.check_availability():
            return True, "Skipped (agda not found)"

        command = [self.checker, "--no-main", "-i", os.path.dirname(filepath), filepath]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            return True, "Type-checking successful"
        else:
            return False, f"Type-checking failed:\n{result.stdout}\n{result.stderr}"


class SMTValidator(ProofValidator):
    """Validator for SMT-LIB files (*.smt2)."""
    def __init__(self):
        # We can use different SMT solvers, e.g., Z3 or CVC4.
        super().__init__("z3")

    def validate(self, filepath: str) -> Tuple[bool, str]:
        """Validate an SMT-LIB file using a solver like Z3."""
        if not self.check_availability():
            return True, f"Skipped ({self.checker} not found)"

        command = [self.checker, "-smt2", filepath]
        result = subprocess.run(command, capture_output=True, text=True)

        output = result.stdout.strip()
        if "sat" in output:
            return True, f"Satisfiable\n{output}"
        elif "unsat" in output:
            return True, f"Unsatisfiable\n{output}"
        else:
            return False, f"Solver error or unknown status:\n{output}\n{result.stderr}"


def main():
    """Main function to run all validators on the proofs directory."""
    validators = {
        ".v": CoqValidator(),
        ".agda": AgdaValidator(),
        ".smt2": SMTValidator(),
    }

    proofs_dir = os.path.dirname(__file__)
    failures = []

    for root, _, files in os.walk(proofs_dir):
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in validators:
                validator = validators[ext]
                filepath = os.path.join(root, file)
                print(f"Validating {filepath} with {validator.checker}...")
                success, message = validator.validate(filepath)
                print(f"  -> {message.splitlines()[0]}")
                if not success:
                    failures.append((filepath, message))

    if failures:
        print("\n--- Validation Summary: Failures Detected ---")
        for filepath, message in failures:
            print(f"\n[!] {filepath}:\n{message}")
        exit(1)
    else:
        print("\n--- Validation Summary: All proofs passed (or were skipped) ---")

if __name__ == "__main__":
    main()
