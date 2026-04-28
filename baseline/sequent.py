from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Sequent:
    left: Tuple[object, ...]
    right: Tuple[object, ...]

    def __str__(self):
        left_side = ", ".join(str(x) for x in self.left)
        right_side = ", ".join(str(x) for x in self.right)
        return f"{left_side} ⊢ {right_side}"