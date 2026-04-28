import time
from parser.parser import FormulaParser
from baseline.sequent import Sequent
from baseline.baseline_solver import BaselineSolver
from improved.improved_solver import ImprovedSolver


DATASETS = [
    "datasets/easy.txt",
    "datasets/medium.txt",
    "datasets/hard.txt",
]


def load_formulas(path):
    with open(path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def test_solver(solver_class, formulas):
    solved = 0
    total_time = 0.0

    for formula in formulas:
        ast = FormulaParser(formula).parse()
        sequent = Sequent(left=(), right=(ast,))

        solver = solver_class(max_depth=150)

        start = time.perf_counter()
        result = solver.prove(sequent)
        end = time.perf_counter()

        if result:
            solved += 1

        total_time += end - start

    return solved, total_time


for dataset in DATASETS:
    formulas = load_formulas(dataset)

    baseline_solved, baseline_time = test_solver(BaselineSolver, formulas)
    improved_solved, improved_time = test_solver(ImprovedSolver, formulas)

    print("Dataset:", dataset)
    print("Total formulas:", len(formulas))
    print("Baseline solved:", baseline_solved)
    print("Improved solved:", improved_solved)
    print("Baseline time:", round(baseline_time, 6))
    print("Improved time:", round(improved_time, 6))
    print()