import unittest
import os
import tempfile
from proofs.coq import generate_coq_script, verify_coq_script

import pytest

class TestCoqIntegration(unittest.TestCase):

    @pytest.mark.skip(reason="coqc not installed in sandbox")
    def test_verify_simple_function(self):
        func_name = "increment"
        func_code = "def increment(x): return x + 1"
        theorem = "increment x = x + 1"

        coq_script = generate_coq_script(func_name, func_code, theorem)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.v', delete=False) as f:
            f.write(coq_script)
            script_path = f.name

        try:
            verified, output = verify_coq_script(script_path)
            self.assertTrue(verified, f"Coq verification failed with output:\n{output}")
        finally:
            os.remove(script_path)

    def test_verify_false_theorem(self):
        func_name = "identity"
        func_code = "def identity(x): return x"
        theorem = "identity x = x + 1" # This is false

        coq_script = generate_coq_script(func_name, func_code, theorem)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.v', delete=False) as f:
            f.write(coq_script)
            script_path = f.name

        try:
            verified, output = verify_coq_script(script_path)
            self.assertFalse(verified, "Coq verification should fail for a false theorem.")
        finally:
            os.remove(script_path)


if __name__ == '__main__':
    unittest.main()
