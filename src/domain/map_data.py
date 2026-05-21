from dataclasses import dataclass

from src.domain.connection import Connection
from src.domain.zone import Zone


@dataclass
class MapData:
    """Store the parsed and validated map definition.

    Attributes:
        nb_drones: Number of drones to route.
        zones: Zones keyed by name.
        connections: Undirected links between zones.
        start_name: Name of the start hub.
        end_name: Name of the destination hub.
    """

    nb_drones: int
    zones: dict[str, Zone]
    connections: list[Connection]
    start_name: str
    end_name: str
