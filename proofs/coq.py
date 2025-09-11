"""
This module provides functions for interacting with the Coq proof assistant.
"""
import subprocess
import os
from typing import Tuple

def generate_coq_script(func_name: str, func_code: str, theorem: str) -> str:
    """
    Generates a Coq script from a Python function and a theorem.
    """
    # Very simple parser for "def fname(x): return expr"
    try:
        return_expr = func_code.split("return")[1].strip()
    except IndexError:
        # Fallback for simple cases
        return_expr = "x"

    coq_code = f"""
Require Import ZArith.
Require Import Lia.
Open Scope Z_scope.

Definition {func_name} (x : Z) : Z := {return_expr}.

Theorem {func_name}_correct : forall (x : Z), {theorem}.
Proof.
  intros.
  unfold {func_name}.
  lia.
Qed.
"""
    return coq_code

def verify_coq_script(script_path: str) -> Tuple[bool, str]:
    """
    Verifies a Coq script using coqc and coqchk.
    """
    try:
        # First, compile the script with coqc
        compile_result = subprocess.run(
            ["coqc", script_path],
            capture_output=True,
            text=True,
        )

        if "Error" in compile_result.stderr or "Error" in compile_result.stdout:
             return False, "coqc compilation failed:\n" + compile_result.stderr + compile_result.stdout

        # Then, check the compiled file with coqchk
        lib_name = os.path.basename(script_path).replace(".v", "")

        # coqchk needs the directory of the .vo file in the load path
        check_result = subprocess.run(
            ["coqchk", "-R", os.path.dirname(script_path), "", lib_name],
            capture_output=True,
            text=True,
        )

        return check_result.returncode == 0, check_result.stdout + check_result.stderr

    except FileNotFoundError as e:
        return False, f"{e.filename} not found. Please ensure Coq is installed and in your PATH."
    finally:
        # Clean up generated files
        vo_path = script_path.replace(".v", ".vo")
        if os.path.exists(vo_path):
            os.remove(vo_path)
        glob_path = script_path.replace(".v", ".glob")
        if os.path.exists(glob_path):
            os.remove(glob_path)
