import z3
from z3 import Z3Exception
from typing import Any, Dict, List, Optional

from core.types import SMTResult, ProofCertificate

class ConstraintSolver:
    """
    A wrapper around the Z3 SMT solver for constraint satisfaction problems.
    """

    def __init__(self, proof_generation: bool = False):
        """
        Initializes the ConstraintSolver.

        Args:
            proof_generation: If True, configures the solver to generate proofs.
        """
        self.context = z3.Context()
        self.solver = z3.Solver(ctx=self.context)
        self.variables: Dict[str, z3.ExprRef] = {}
        if proof_generation:
            self.solver.set(proof=True)

    def add_variable(self, name: str, var_type: str):
        if name in self.variables:
            raise ValueError(f"Variable '{name}' already exists.")
        var_constructor = getattr(z3, f"{var_type}", None)
        if not var_constructor:
            raise ValueError(f"Unsupported variable type: {var_type}")
        self.variables[name] = var_constructor(name, ctx=self.context)

    def add_constraint(self, expression: z3.BoolRef):
        if not isinstance(expression, z3.BoolRef):
            raise TypeError("Constraint must be a Z3 boolean expression.")
        self.solver.add(expression)

    def check_satisfiability(self) -> SMTResult:
        result = self.solver.check()
        if result == z3.sat:
            model = self.get_model(self.solver.model())
            return SMTResult(satisfiable=True, model=model)
        elif result == z3.unsat:
            return SMTResult(satisfiable=False, model=None)
        else:
            return SMTResult(satisfiable=False, model=None)

    def get_model(self, model: z3.ModelRef) -> Optional[Dict[str, Any]]:
        if model is None:
            return None
        model_dict = {}
        for var_name, var in self.variables.items():
            interp = model.get_interp(var)
            if interp is not None:
                if z3.is_int_value(interp):
                    model_dict[var_name] = interp.as_long()
                elif z3.is_real_value(interp):
                    model_dict[var_name] = float(interp.as_decimal(10))
                elif z3.is_bool(interp):
                    model_dict[var_name] = bool(interp)
                else:
                    model_dict[var_name] = str(interp)
        return model_dict

    def generate_proof_certificate(self) -> Optional[ProofCertificate]:
        """
        Generates a proof certificate if the constraints are unsatisfiable.
        """
        try:
            proof = self.solver.proof()
            return ProofCertificate(
                content=str(proof),
                verifier="Z3",
                assumptions=[str(a) for a in self.solver.assertions()]
            )
        except Z3Exception:
            # This can happen if check() was not called, or if it was not unsat.
            return None

    def reset(self):
        self.solver.reset()
        self.variables.clear()

    def get_variable(self, name: str) -> z3.ExprRef:
        if name not in self.variables:
            raise KeyError(f"Variable '{name}' not found.")
        return self.variables[name]

# Example usage:
if __name__ == '__main__':
    print("--- Satisfiable Example ---")
    solver_sat = ConstraintSolver()
    solver_sat.add_variable('x', 'Int')
    solver_sat.add_variable('y', 'Int')
    x = solver_sat.get_variable('x')
    y = solver_sat.get_variable('y')
    solver_sat.add_constraint(x > 0)
    solver_sat.add_constraint(y > x)
    solver_sat.add_constraint(y < 5)
    result = solver_sat.check_satisfiability()
    print(f"Is satisfiable? {result.satisfiable}")
    if result.satisfiable:
        print(f"Model: {result.model}")

    print("\n--- Unsatisfiable Example with Proof ---")
    solver_unsat = ConstraintSolver(proof_generation=True)
    solver_unsat.add_variable('a', 'Bool')
    a = solver_unsat.get_variable('a')
    solver_unsat.add_constraint(a)
    solver_unsat.add_constraint(z3.Not(a))

    result_unsat = solver_unsat.check_satisfiability()
    print(f"Is satisfiable? {result_unsat.satisfiable}")

    if not result_unsat.satisfiable:
        proof = solver_unsat.generate_proof_certificate()
        if proof:
            print("Proof certificate generated successfully.")
        else:
            print("Failed to generate proof certificate.")
