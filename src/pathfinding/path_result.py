from dataclasses import dataclass


@dataclass
class PathResult:
    """Store a path and its real movement cost.

    Attributes:
        zones: Ordered zone names from start to end.
        cost: Total movement cost for the path.
    """

    zones: list[str]
    cost: int
