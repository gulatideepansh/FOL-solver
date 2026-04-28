from parser.parser import Not, And, Or, Implies, ForAll, Exists, Const, Predicate
from baseline.sequent import Sequent
from baseline.substitution import substitute_formula


class BaselineSolver:
    def __init__(self, max_depth=50):
        self.max_depth = max_depth
        self.fresh_counter = 0

    def fresh_const(self):
        name = f"c{self.fresh_counter}"
        self.fresh_counter += 1
        return Const(name)

    def collect_constants_from_term(self, term):
        if isinstance(term, Const):
            return {term}
        return set()

    def collect_constants_from_formula(self, formula):
        constants = set()

        if isinstance(formula, Predicate):
            for arg in formula.args:
                constants |= self.collect_constants_from_term(arg)

        elif isinstance(formula, Not):
            constants |= self.collect_constants_from_formula(formula.formula)

        elif isinstance(formula, (And, Or, Implies)):
            constants |= self.collect_constants_from_formula(formula.left)
            constants |= self.collect_constants_from_formula(formula.right)

        elif isinstance(formula, (ForAll, Exists)):
            constants |= self.collect_constants_from_formula(formula.body)

        return constants

    def constants_in_sequent(self, sequent):
        constants = set()

        for formula in sequent.left + sequent.right:
            constants |= self.collect_constants_from_formula(formula)

        if not constants:
            constants.add(Const("a"))

        return constants

    def is_closed(self, sequent):
        for left_formula in sequent.left:
            if left_formula in sequent.right:
                return True
        return False

    def remove_left(self, sequent, formula):
        left = list(sequent.left)
        left.remove(formula)
        return tuple(left)

    def remove_right(self, sequent, formula):
        right = list(sequent.right)
        right.remove(formula)
        return tuple(right)

    def prove(self, sequent, depth=0):
        if depth > self.max_depth:
            return False

        if self.is_closed(sequent):
            return True

        # ---------- LEFT RULES ----------

        for formula in sequent.left:

            if isinstance(formula, Not):
                new_left = self.remove_left(sequent, formula)
                new_right = sequent.right + (formula.formula,)
                return self.prove(Sequent(new_left, new_right), depth + 1)

            if isinstance(formula, And):
                new_left = self.remove_left(sequent, formula) + (formula.left, formula.right)
                return self.prove(Sequent(new_left, sequent.right), depth + 1)

            if isinstance(formula, Or):
                new_left = self.remove_left(sequent, formula)
                left_branch = Sequent(new_left + (formula.left,), sequent.right)
                right_branch = Sequent(new_left + (formula.right,), sequent.right)
                return self.prove(left_branch, depth + 1) and self.prove(right_branch, depth + 1)

            if isinstance(formula, Implies):
                new_left = self.remove_left(sequent, formula)
                left_branch = Sequent(new_left, sequent.right + (formula.left,))
                right_branch = Sequent(new_left + (formula.right,), sequent.right)
                return self.prove(left_branch, depth + 1) and self.prove(right_branch, depth + 1)

            if isinstance(formula, ForAll):
                new_left = self.remove_left(sequent, formula)

                for const in self.constants_in_sequent(sequent):
                    instantiated = substitute_formula(formula.body, formula.var, const)
                    if self.prove(Sequent(new_left + (instantiated,), sequent.right), depth + 1):
                        return True

                return False

            if isinstance(formula, Exists):
                new_left = self.remove_left(sequent, formula)
                fresh = self.fresh_const()
                instantiated = substitute_formula(formula.body, formula.var, fresh)
                return self.prove(Sequent(new_left + (instantiated,), sequent.right), depth + 1)

        # ---------- RIGHT RULES ----------

        for formula in sequent.right:

            if isinstance(formula, Not):
                new_right = self.remove_right(sequent, formula)
                new_left = sequent.left + (formula.formula,)
                return self.prove(Sequent(new_left, new_right), depth + 1)

            if isinstance(formula, And):
                new_right = self.remove_right(sequent, formula)
                left_branch = Sequent(sequent.left, new_right + (formula.left,))
                right_branch = Sequent(sequent.left, new_right + (formula.right,))
                return self.prove(left_branch, depth + 1) and self.prove(right_branch, depth + 1)

            if isinstance(formula, Or):
                new_right = self.remove_right(sequent, formula) + (formula.left, formula.right)
                return self.prove(Sequent(sequent.left, new_right), depth + 1)

            if isinstance(formula, Implies):
                new_right = self.remove_right(sequent, formula) + (formula.right,)
                new_left = sequent.left + (formula.left,)
                return self.prove(Sequent(new_left, new_right), depth + 1)

            if isinstance(formula, ForAll):
                new_right = self.remove_right(sequent, formula)
                fresh = self.fresh_const()
                instantiated = substitute_formula(formula.body, formula.var, fresh)
                return self.prove(Sequent(sequent.left, new_right + (instantiated,)), depth + 1)

            if isinstance(formula, Exists):
                new_right = self.remove_right(sequent, formula)

                for const in self.constants_in_sequent(sequent):
                    instantiated = substitute_formula(formula.body, formula.var, const)
                    if self.prove(Sequent(sequent.left, new_right + (instantiated,)), depth + 1):
                        return True

                return False

        return False