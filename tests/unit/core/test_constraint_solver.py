import unittest
import z3
from core.constraint_solver import ConstraintSolver

class TestConstraintSolver(unittest.TestCase):

    def setUp(self):
        self.solver = ConstraintSolver()

    def test_solve_simple_sat(self):
        constraints = ["x > 5", "y < 10", "x + y == 14"]
        variables = {"x": z3.IntSort(), "y": z3.IntSort()}
        self.assertTrue(self.solver.solve(constraints, variables))

    def test_solve_simple_unsat(self):
        constraints = ["x > 5", "x < 5"]
        variables = {"x": z3.IntSort()}
        self.assertFalse(self.solver.solve(constraints, variables))

    def test_solve_with_reals(self):
        constraints = ["x > 5.5", "y < 10.2", "x + y > 15.6"]
        variables = {"x": z3.RealSort(), "y": z3.RealSort()}
        self.assertTrue(self.solver.solve(constraints, variables))

    def test_solve_with_booleans(self):
        constraints = ["p", "Or(Not(p), q)"]
        variables = {"p": z3.BoolSort(), "q": z3.BoolSort()}
        self.assertTrue(self.solver.solve(constraints, variables))

    def test_solve_with_quantifiers(self):
        x = z3.Int('x')
        constraints = ["ForAll([x], Implies(x > 0, x + 1 > x))"]
        variables = {"x": z3.IntSort()}
        self.assertTrue(self.solver.solve(constraints, variables))

    def test_solve_with_functions(self):
        f = z3.Function('f', z3.IntSort(), z3.IntSort())
        x = z3.Int('x')
        constraints = ["f(x) > x", "f(x) < x + 2"]
        variables = {"x": z3.IntSort(), "f": f}
        self.assertTrue(self.solver.solve(constraints, variables))

    def test_invalid_constraint(self):
        constraints = ["x > 5", "y < 10", "x @ y == 14"] # invalid operator
        variables = {"x": z3.IntSort(), "y": z3.IntSort()}
        self.assertFalse(self.solver.solve(constraints, variables))

if __name__ == '__main__':
    unittest.main()
