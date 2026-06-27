from typing import Optional


def length_or_zero(s: Optional[str]) -> int:
    if s is not None:
        return len(s)
    return 0
