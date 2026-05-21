from src.graph.graph import Graph
from src.pathfinding.path_result import PathResult
from src.domain.connection import Connection
from src.domain.zone import ZoneType


class PathAssigner:
    """Assign discovered paths to drones using path cost and capacity."""

    def __init__(self, graph: Graph, paths: list[PathResult]) -> None:
        """Create a path assigner.

        Args:
            graph: Graph containing drone count and capacity data.
            paths: Candidate path results available for assignment.
        """
        self.graph = graph
        self.paths = paths
        self.nb_drones = self.graph.get_nb_drones()

    def assign(self) -> list[list[str]]:
        """Assign one path to each drone.

        Returns:
            A list of zone-name paths, one per drone.
        """
        paths_assigned: list[list[str]] = []
        assigned_counts: dict[int, int] = {}
        for _ in range(self.nb_drones):
            best_path_index = self._get_best_path_index(assigned_counts)
            best_path = self.paths[best_path_index]
            paths_assigned.append(best_path.zones)
            assigned_counts[best_path_index] = (
                assigned_counts.get(best_path_index, 0) + 1
            )
        return paths_assigned

    def _get_best_path_index(self, assigned_counts: dict[int, int]) -> int:
        """Return the currently best-scoring candidate path index."""
        best_path = 0
        min_score = self._estimate_path_score(best_path, assigned_counts)

        for index in range(1, len(self.paths)):
            curr_score = self._estimate_path_score(index, assigned_counts)
            if curr_score < min_score:
                min_score = curr_score
                best_path = index

        return best_path

    def _estimate_path_score(
            self,
            path_index: int,
            assigned_counts: dict[int, int]
    ) -> float:
        """Estimate assignment score for one candidate path."""
        path = self.paths[path_index]
        bottleneck = self._get_path_bottleneck(path)
        congestion_penalty = (
            assigned_counts.get(path_index, 0) / bottleneck
        )
        priority_bonus = self._get_priority_bonus(path)
        score = path.cost + congestion_penalty - priority_bonus
        return score

    def _get_path_bottleneck(self, path: PathResult) -> int:
        """Return the smallest zone or link capacity along a path."""
        length = len(path.zones)
        connections: list[Connection] = self._get_path_connections(
            path.zones, length
        )
        weak_point = connections[0].max_link_capacity

        for connection in connections:
            if connection.max_link_capacity < weak_point:
                weak_point = connection.max_link_capacity

        start_name, end_name = self.graph.get_start_end()

        for zone_name in path.zones:
            if zone_name == start_name or zone_name == end_name:
                continue
            zone = self.graph.get_zone(zone_name)
            if zone.max_drones < weak_point:
                weak_point = zone.max_drones

        return weak_point

    def _get_path_connections(
            self,
            path: list[str],
            length: int
    ) -> list[Connection]:
        """Return graph connections used by an ordered zone path."""
        connections: list[Connection] = []

        for index in range(1, length):
            connections.append(
                self.graph.get_connection(path[index - 1], path[index])
            )

        return connections

    def _get_priority_bonus(self, path: PathResult) -> float:
        """Return the score bonus contributed by priority zones."""
        count = 0
        start_name, end_name = self.graph.get_start_end()

        for z in path.zones:
            if z == start_name or z == end_name:
                continue
            zone = self.graph.get_zone(z)
            if zone.zone_type == ZoneType.PRIORITY:
                count += 1

        return count * 0.1
