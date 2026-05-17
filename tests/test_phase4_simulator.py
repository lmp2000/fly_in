"""Manual runner for Phase 4 basic simulation."""

from src.graph.graph import Graph
from src.parser.map_parser import MapParser
from src.pathfinding.path_finder import PathFinder
from src.simulation.simulator import Simulator


def main() -> None:
    """Run a simple Phase 4 simulation using the existing project flow."""
    parser = MapParser()
    map_data = parser.parse_file("maps/phase4_simple_fork.txt")

    graph = Graph(map_data)
    path_finder = PathFinder(graph)
    path_results = path_finder.find_candidate_paths(max_paths=2)
    paths = [result.zones for result in path_results]

    print("Discovered paths:")
    for path in paths:
        print(path)

    simulator = Simulator(graph, paths)
    turns = simulator.simulate()

    print("\nSimulation output:")
    for turn in turns:
        print(turn)


if __name__ == "__main__":
    main()
