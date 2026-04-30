from dataclasses import dataclass

from src.domain.connection import Connection
from src.domain.zone import Zone


@dataclass
class MapData:
    nb_drones: int
    zones: dict[str, Zone]
    connections: list[Connection]
    start_name: str
    end_name: str