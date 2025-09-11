"""
A simple constraint solver.
"""
from typing import List, Dict, Any

class ConstraintSolver:
    """
    A simple constraint solver that can handle simple inequalities.
    """
    def solve(self, constraints: List[str], variables: Dict[str, Any]) -> bool:
        """
        Solves a set of constraints.
        """
        for constraint in constraints:
            parts = constraint.split()
            if len(parts) != 3:
                return False

            var, op, val = parts
            if var not in variables:
                return False

            if op == "<=":
                if not variables[var] <= float(val):
                    return False
            elif op == ">=":
                if not variables[var] >= float(val):
                    return False
            elif op == "<":
                if not variables[var] < float(val):
                    return False
            elif op == ">":
                if not variables[var] > float(val):
                    return False
            elif op == "==":
                if not variables[var] == float(val):
                    return False
            else:
                return False
        return True
