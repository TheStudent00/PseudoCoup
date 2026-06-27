from typing import List, Optional
import math


def arithmetic() -> int:
    a: int = 3 * 4 + 1
    return a


def if_else(a: int) -> str:
    if a > 0:
        return "p"
    else:
        return "n"


def ternary(a: int) -> int:
    y: int = 1 if a > 0 else -1
    return y


def for_range(n: int) -> int:
    total: int = 0
    for i in range(n):
        total += i
    return total


def while_loop(k: int) -> int:
    while k > 0:
        k -= 1
    return k


def list_ops() -> int:
    xs: List[int] = [1, 2, 3]
    xs.append(4)
    return len(xs)


def null_check(z: Optional[int]) -> str:
    if z is None:
        return "z"
    return "v"


class Pt:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def dist(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)
