from dataclasses import dataclass
from typing import List


# ---------- AST NODES ----------

@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Const:
    name: str


@dataclass(frozen=True)
class Predicate:
    name: str
    args: List[object]


@dataclass(frozen=True)
class Not:
    formula: object


@dataclass(frozen=True)
class And:
    left: object
    right: object


@dataclass(frozen=True)
class Or:
    left: object
    right: object


@dataclass(frozen=True)
class Implies:
    left: object
    right: object


@dataclass(frozen=True)
class ForAll:
    var: str
    body: object


@dataclass(frozen=True)
class Exists:
    var: str
    body: object


# ---------- TOKENISER ----------

def tokenize(text: str) -> list[str]:
    replacements = {
        "(": " ( ",
        ")": " ) ",
        ",": " , ",
        ".": " . ",
        "&": " & ",
        "|": " | ",
        "->": " -> ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text.split()


# ---------- PARSER ----------

class FormulaParser:
    def __init__(self, text: str):
        self.tokens = tokenize(text)
        self.pos = 0

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected=None):
        token = self.current()

        if expected is not None and token != expected:
            raise SyntaxError(f"Expected {expected}, got {token}")

        self.pos += 1
        return token

    def parse(self):
        result = self.parse_implication()

        if self.current() is not None:
            raise SyntaxError(f"Unexpected token: {self.current()}")

        return result

    def parse_implication(self):
        left = self.parse_or()

        if self.current() == "->":
            self.consume("->")
            right = self.parse_implication()
            return Implies(left, right)

        return left

    def parse_or(self):
        left = self.parse_and()

        while self.current() == "|":
            self.consume("|")
            right = self.parse_and()
            left = Or(left, right)

        return left

    def parse_and(self):
        left = self.parse_unary()

        while self.current() == "&":
            self.consume("&")
            right = self.parse_unary()
            left = And(left, right)

        return left

    def parse_unary(self):
        token = self.current()

        if token == "not":
            self.consume("not")
            return Not(self.parse_unary())

        if token == "forall":
            self.consume("forall")
            var = self.consume()
            self.consume(".")
            return ForAll(var, self.parse_implication())

        if token == "exists":
            self.consume("exists")
            var = self.consume()
            self.consume(".")
            return Exists(var, self.parse_implication())

        if token == "(":
            self.consume("(")
            formula = self.parse_implication()
            self.consume(")")
            return formula

        return self.parse_predicate()

    def parse_term(self):
        name = self.consume()

        if name is None:
            raise SyntaxError("Unexpected end while parsing term")

        if name in {"x", "y", "z", "u", "v", "w"}:
            return Var(name)

        return Const(name)
    
    def parse_predicate(self):
        name = self.consume()

        self.consume("(")

        args = []

        if self.current() != ")":
            args.append(self.parse_term())

            while self.current() == ",":
                self.consume(",")
                args.append(self.parse_term())

        self.consume(")")

        return Predicate(name, args)