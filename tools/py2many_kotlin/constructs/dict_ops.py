from typing import Dict


def count_get(d: Dict[str, int], key: str) -> int:
    if key in d:
        return d[key]
    return 0
