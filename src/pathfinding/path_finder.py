from src.graph.graph import Graph
from src.pathfinding.dijkstra import Dijkstra
from src.pathfinding.path_result import PathResult
from src.pathfinding.path_error import PathError


class PathFinder:
    """Generate candidate paths for drone assignment."""

    def __init__(self, graph: Graph) -> None:
        """Create a candidate path finder.

        Args:
            graph: Graph used for pathfinding.
        """
        self.graph = graph

    def find_candidate_paths(self, max_paths: int) -> list[PathResult]:
        """Find candidate paths while discouraging repeated zones.

        Args:
            max_paths: Maximum number of paths to collect.

        Returns:
            A non-empty list of candidate path results.

        Raises:
            PathError: If no route from start to end can be found.
        """
        paths: list[PathResult] = []
        penalties: dict[str, float] = {}
        start, end = self.graph.get_start_end()
        dijkstra = Dijkstra(self.graph)

        for _ in range(max_paths):
            new = dijkstra.find_path(penalties)
            is_duplicate: bool = any(path.zones == new.zones for path in paths)
            if is_duplicate:
                for zone in new.zones:
                    if zone == start or zone == end:
                        continue
                    if zone in penalties:
                        penalties[zone] += 5
                    else:
                        penalties[zone] = 5
                continue
            paths.append(new)
            for zone in new.zones:
                if zone == start or zone == end:
                    continue
                if zone in penalties:
                    penalties[zone] += 3
                else:
                    penalties[zone] = 3

        if len(paths) == 0:
            raise PathError(
                "There are no available paths from start to end in this map"
            )

        return paths
