from src.domain.connection import Connection
from src.domain.map_data import MapData
from src.domain.zone import Zone, ZoneType
from src.graph.graph_error import GraphError


class Graph:
    """Represent the drone map as an adjacency graph.

    The graph exposes zone and connection lookup helpers used by the
    pathfinding and simulation layers.
    """

    def __init__(self, map_data: MapData) -> None:
        """Build a graph from parsed map data.

        Args:
            map_data: Parsed map definition.
        """
        self.map_data = map_data
        self.adjacency_list: dict[str, list[str]] = {}
        self._init_adjacency_list()
        self._add_connections()

    def _init_adjacency_list(self) -> None:
        for zone in self.map_data.zones.values():
            self.adjacency_list[zone.name] = []

    def _add_connections(self) -> None:
        for connection in self.map_data.connections:
            self.adjacency_list[connection.zone_a].append(
                connection.zone_b
            )
            self.adjacency_list[connection.zone_b].append(
                connection.zone_a
            )

    def get_neighbors(self, zone_name: str) -> list[str]:
        """Return the walkable neighbors of a zone.

        Args:
            zone_name: Name of the zone whose neighbors should be returned.

        Returns:
            A list of adjacent walkable zone names.

        Raises:
            GraphError: If the zone does not exist.
        """
        if zone_name not in self.adjacency_list:
            raise GraphError(
                "Zone name does not exist in current map"
            )
        valid_neighbors = [
            neighbor for neighbor in self.adjacency_list[zone_name]
            if self.is_walkable(neighbor)
        ]
        return valid_neighbors

    def get_zone(self, zone_name: str) -> Zone:
        """Return a zone by name.

        Args:
            zone_name: Name of the zone to retrieve.

        Returns:
            The matching Zone object.

        Raises:
            GraphError: If the zone does not exist.
        """
        if zone_name not in self.map_data.zones:
            raise GraphError(
                "Zone name does not exist in current map"
            )
        return self.map_data.zones[zone_name]

    def is_walkable(self, zone_name: str) -> bool:
        """Return whether a zone can be traversed.

        Args:
            zone_name: Name of the zone to inspect.

        Returns:
            True when the zone can be used by pathfinding.
        """
        zone = self.get_zone(zone_name)
        match zone.zone_type:
            case ZoneType.NORMAL:
                return True
            case ZoneType.PRIORITY:
                return True
            case ZoneType.RESTRICTED:
                return True
            case ZoneType.BLOCKED:
                return False
            case _:
                return False

    def movement_cost(self, destination_zone_name: str) -> int:
        """Return the cost of entering a destination zone.

        Args:
            destination_zone_name: Name of the zone being entered.

        Returns:
            Movement cost for the destination zone.

        Raises:
            GraphError: If the zone is missing, blocked, or invalid.
        """
        if destination_zone_name not in self.map_data.zones:
            raise GraphError(
                "Destination zone name does not exist in current map"
            )
        if not self.is_walkable(destination_zone_name):
            raise GraphError(
                "Zone is blocked or not achievable"
            )
        zone = self.get_zone(destination_zone_name)
        zone_type = zone.zone_type
        match zone_type:
            case ZoneType.NORMAL:
                return 1
            case ZoneType.PRIORITY:
                return 1
            case ZoneType.RESTRICTED:
                return 2
            case _:
                raise GraphError(
                    "Destination zone does not have a valid type"
                )

    def get_connection(self, zone_a: str, zone_b: str) -> Connection:
        """Return the connection between two zones.

        Args:
            zone_a: Name of the first endpoint.
            zone_b: Name of the second endpoint.

        Returns:
            The connection linking both zones.

        Raises:
            GraphError: If either zone or the connection does not exist.
        """
        if zone_a not in self.map_data.zones:
            raise GraphError(
                "Invalid Zone A"
            )
        if zone_b not in self.map_data.zones:
            raise GraphError(
                "Invalid Zone B"
            )
        target_key = tuple(sorted((zone_a, zone_b)))

        connection = next(
            (
                c for c in self.map_data.connections
                if c.key() == target_key
            ), None
        )

        if not connection:
            raise GraphError(
                "There is no connection for the 2 zones provided"
            )

        return connection

    def get_zone_names(self) -> list[str]:
        """Return all zone names in the graph.

        Returns:
            A list of zone names.
        """
        result: list[str] = []
        for zone in self.map_data.zones:
            result.append(zone)
        return result

    def get_start_end(self) -> tuple[str, str]:
        """Return the start and end hub names.

        Returns:
            A tuple containing the start hub and end hub names.
        """
        return (
            self.map_data.start_name, self.map_data.end_name
        )

    def get_nb_drones(self) -> int:
        """Return the number of drones declared for the map.

        Returns:
            The map drone count.
        """
        return self.map_data.nb_drones
