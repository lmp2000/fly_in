import heapq

from src.graph.graph import Graph
from src.graph.graph_error import GraphError
from src.pathfinding.path_result import PathResult
from src.pathfinding.path_error import PathError


class Dijkstra:
    """Find the lowest-cost route through the graph."""

    def __init__(self, graph: Graph) -> None:
        """Create a path finder for a graph.

        Args:
            graph: Graph used for zone and movement-cost lookups.
        """
        self.graph = graph

    def find_path(
            self, zone_penalties: dict[str, float] | None = None
    ) -> PathResult:
        """Find the lowest-cost path from start hub to end hub.

        Args:
            zone_penalties: Optional extra costs applied to named zones.

        Returns:
            The selected path and its real movement cost.

        Raises:
            PathError: If the graph endpoints are invalid or unreachable.
        """
        try:
            start, end = self.graph.get_start_end()
        except GraphError as error:
            raise PathError(
                "Please select only zones that exist in the map"
            ) from error

        distances: dict[str, float] = {}
        for zone in self.graph.get_zone_names():
            distances[zone] = float("inf")
        distances[start] = 0

        if zone_penalties is None:
            zone_penalties = {}

        previous: dict[str, str | None] = {}
        for zone in self.graph.get_zone_names():
            previous[zone] = None

        priority_queue: list[tuple[float, str]] = []
        heapq.heappush(priority_queue, (0, start))

        while priority_queue:
            curr_cost, curr_name = heapq.heappop(priority_queue)
            if curr_cost > distances[curr_name]:
                continue
            if curr_name == end:
                break
            neighbors = self.graph.get_neighbors(curr_name)
            for neighbor in neighbors:
                n_cost = self.graph.movement_cost(neighbor)
                total_cost = n_cost + curr_cost
                if neighbor in zone_penalties:
                    penalty = zone_penalties.get(neighbor, 0)
                    total_cost += penalty
                if total_cost >= distances[neighbor]:
                    continue
                distances[neighbor] = total_cost
                previous[neighbor] = curr_name
                heapq.heappush(priority_queue, (total_cost, neighbor))

        if distances[end] == float("inf"):
            raise PathError(
                "The end goal is not reachable in this map"
            )

        path: list[str] = []
        curr: str | None = end
        while curr is not None:
            path.append(curr)
            curr = previous[curr]
        path.reverse()

        cost = self._calculate_real_cost(path)

        return PathResult(path, cost)

    def _calculate_real_cost(self, path: list[str]) -> int:
        """Calculate the real movement cost for a path."""
        real_cost = 0
        for zone in path[1:]:
            real_cost += self.graph.movement_cost(zone)
        return real_cost
