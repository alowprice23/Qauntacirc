"""
A constraint solver using the Z3 SMT solver.
"""
from typing import List, Dict, Union
import z3

class ConstraintSolver:
    """
    A constraint solver that uses the Z3 SMT solver to handle complex constraints.
    """
    def solve(self, constraints: List[str], variables: Dict[str, Union[z3.SortRef, z3.FuncDeclRef]]) -> bool:
        """
        Solves a set of constraints using the Z3 solver.

        The `variables` dict should map variable names to their Z3 types,
        e.g., {"x": z3.IntSort(), "y": z3.RealSort(), "f": z3.Function('f', z3.IntSort(), z3.IntSort())}.

        The constraint strings are evaluated using `eval`, which is a security risk if the
        constraints are not from a trusted source. The context for eval is limited to the
        Z3 variables and Z3 functions.
        """
        solver = z3.Solver()

        # Declare variables and functions
        z3_context = {}
        for name, sort_or_func in variables.items():
            if isinstance(sort_or_func, z3.SortRef):
                z3_context[name] = z3.Const(name, sort_or_func)
            elif isinstance(sort_or_func, z3.FuncDeclRef):
                z3_context[name] = sort_or_func

        # Add Z3 functions to context
        z3_context.update({
            'And': z3.And, 'Or': z3.Or, 'Not': z3.Not, 'Implies': z3.Implies,
            'ForAll': z3.ForAll, 'Exists': z3.Exists,
        })

        for constraint_str in constraints:
            try:
                # Using eval is a security risk, but allows for complex expressions.
                # A proper parser would be a better solution in a production environment.
                solver.add(eval(constraint_str, z3_context))
            except Exception as e:
                # If parsing fails, the constraint is considered invalid.
                return False

        return solver.check() == z3.sat
