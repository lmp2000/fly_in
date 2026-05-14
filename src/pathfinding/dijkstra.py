import heapq

from src.graph.graph import Graph
from src.graph.graph_error import GraphError
from src.pathfinding.path_result import PathResult
from src.pathfinding.path_error import PathError


class Dijkstra:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def find_path(self, start: str, end: str) -> PathResult:
        try:
            self.graph.get_zone(start)
            self.graph.get_zone(end)
        except GraphError as error:
            raise PathError(
                "Please select only zones that exist in the map"
            ) from error

        distances: dict[str, float] = {}
        for zone in self.graph.get_zone_names():
            distances[zone] = float("inf")
        distances[start] = 0

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

        cost = int(distances[end])

        return PathResult(path, cost)
