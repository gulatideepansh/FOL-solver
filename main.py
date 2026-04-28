from parser.parser import FormulaParser
from baseline.sequent import Sequent
from baseline.baseline_solver import BaselineSolver
from improved.improved_solver import ImprovedSolver


tests = [
    "R(a) -> R(a)",
    "(forall x. R(x)) -> R(a)",
    "R(a) -> exists x. R(x)",
    "(forall x. (R1(x) -> R2(x))) -> ((forall x. R1(x)) -> (forall x. R2(x)))",
]

for formula in tests:
    ast = FormulaParser(formula).parse()
    sequent = Sequent(left=(), right=(ast,))

    baseline = BaselineSolver(max_depth=100)
    improved = ImprovedSolver(max_depth=100)

    baseline_result = baseline.prove(sequent)
    improved_result = improved.prove(sequent)

    print("Formula:", formula)
    print("Baseline:", baseline_result)
    print("Improved:", improved_result)
    print()