from src.graph.graph import Graph
from src.parser.map_parser import MapParser
from src.pathfinding.dijkstra import Dijkstra


def main() -> None:
    """Run a Phase 2 pathfinding example."""
    parser = MapParser()
    map_data = parser.parse_file("maps/phase2_restricted_vs_normal.txt")

    graph = Graph(map_data)
    dijkstra = Dijkstra(graph)

    result = dijkstra.find_path()

    print("Best path:")
    print(" -> ".join(result.zones))
    print(f"Total cost: {result.cost}")


if __name__ == "__main__":
    main()
