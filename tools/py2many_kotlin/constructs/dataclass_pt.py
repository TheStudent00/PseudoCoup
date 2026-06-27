from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int

    def manhattan(self) -> int:
        return abs(self.x) + abs(self.y)
