from dataclasses import dataclass
from enum import Enum


class ZoneType(Enum):
    """Enumerate the supported zone behavior types."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


@dataclass
class Zone:
    """Represent a named map zone with coordinates and constraints.

    Attributes:
        name: Unique zone name.
        x: Horizontal map coordinate.
        y: Vertical map coordinate.
        zone_type: Movement behavior for the zone.
        color: Optional display color metadata.
        max_drones: Maximum drones allowed in the zone at once.
    """

    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    color: str | None = None
    max_drones: int = 1
