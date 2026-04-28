from baseline.baseline_solver import BaselineSolver
from baseline.sequent import Sequent
from parser.parser import ForAll, Exists, Const
from baseline.substitution import substitute_formula


class ImprovedSolver(BaselineSolver):
    def __init__(self, max_depth=150):
        super().__init__(max_depth=max_depth)
        self.visited = set()

    def sequent_key(self, sequent):
        left_key = tuple(sorted(str(x) for x in sequent.left))
        right_key = tuple(sorted(str(x) for x in sequent.right))
        return left_key, right_key

    def prove(self, sequent, depth=0):
        if depth > self.max_depth:
            return False

        key = self.sequent_key(sequent)
        if key in self.visited:
            return False
        self.visited.add(key)

        # Extra improvement:
        # If left has forall and right has forall, use the same fresh constant.
        for left_formula in sequent.left:
            if isinstance(left_formula, ForAll):
                for right_formula in sequent.right:
                    if isinstance(right_formula, ForAll):
                        c = Const("a")

                        new_left_formula = substitute_formula(
                            left_formula.body,
                            left_formula.var,
                            c
                        )

                        new_right_formula = substitute_formula(
                            right_formula.body,
                            right_formula.var,
                            c
                        )

                        new_left = tuple(
                            f for f in sequent.left if f != left_formula
                        ) + (new_left_formula,)

                        new_right = tuple(
                            f for f in sequent.right if f != right_formula
                        ) + (new_right_formula,)

                        if self.prove(Sequent(new_left, new_right), depth + 1):
                            return True

        return super().prove(sequent, depth)