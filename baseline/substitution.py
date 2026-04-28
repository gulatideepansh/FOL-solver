from parser.parser import Var, Const, Predicate, Not, And, Or, Implies, ForAll, Exists


def substitute_term(term, var_name, replacement):
    if isinstance(term, Var) and term.name == var_name:
        return replacement

    return term


def substitute_formula(formula, var_name, replacement):
    if isinstance(formula, Predicate):
        new_args = [
            substitute_term(arg, var_name, replacement)
            for arg in formula.args
        ]
        return Predicate(formula.name, new_args)

    if isinstance(formula, Not):
        return Not(substitute_formula(formula.formula, var_name, replacement))

    if isinstance(formula, And):
        return And(
            substitute_formula(formula.left, var_name, replacement),
            substitute_formula(formula.right, var_name, replacement)
        )

    if isinstance(formula, Or):
        return Or(
            substitute_formula(formula.left, var_name, replacement),
            substitute_formula(formula.right, var_name, replacement)
        )

    if isinstance(formula, Implies):
        return Implies(
            substitute_formula(formula.left, var_name, replacement),
            substitute_formula(formula.right, var_name, replacement)
        )

    if isinstance(formula, ForAll):
        if formula.var == var_name:
            return formula
        return ForAll(formula.var, substitute_formula(formula.body, var_name, replacement))

    if isinstance(formula, Exists):
        if formula.var == var_name:
            return formula
        return Exists(formula.var, substitute_formula(formula.body, var_name, replacement))

    return formula