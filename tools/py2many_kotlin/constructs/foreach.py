from typing import List


def sum_list(xs: List[int]) -> int:
    total: int = 0
    for x in xs:
        total += x
    return total
