from dataclasses import dataclass


@dataclass
class PathResult:
    zones: list[str]
    cost: int