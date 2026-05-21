from dataclasses import dataclass
from typing import cast


@dataclass
class Connection:
    """Represent an undirected link between two zones.

    Attributes:
        zone_a: Name of one endpoint zone.
        zone_b: Name of the other endpoint zone.
        max_link_capacity: Maximum drones that can use the link per turn.
    """

    zone_a: str
    zone_b: str
    max_link_capacity: int = 1

    def key(self) -> tuple[str, str]:
        """Return a stable undirected key for the connection.

        Returns:
            The two endpoint names sorted as a tuple.
        """
        return cast(tuple[str, str], tuple(sorted((self.zone_a, self.zone_b))))
