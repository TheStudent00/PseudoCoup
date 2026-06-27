from typing import Tuple


def divmod2(a: int, b: int) -> Tuple[int, int]:
    q: int = a // b
    r: int = a % b
    return (q, r)
