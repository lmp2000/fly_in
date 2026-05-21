import argparse
from pathlib import Path

from src.graph.graph import Graph
from src.parser.map_parser import MapParser
from src.pathfinding.path_finder import PathFinder
from src.simulation.simulator import Simulator


MAPS_ROOT = Path("maps/maps_42")
LEVEL_ORDER = {
    "easy": 0,
    "medium": 1,
    "hard": 2,
    "challenger": 3,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Fly-in simulation.")
    parser.add_argument("map_path", nargs="?")
    parser.add_argument(
        "--visual",
        action="store_true",
        help="Replay the simulation with the optional pygame visualizer.",
    )
    parser.add_argument(
        "--list-maps",
        action="store_true",
        help="List available maps and exit.",
    )
    return parser.parse_args()


def discover_maps() -> list[Path]:
    if not MAPS_ROOT.exists():
        return []

    paths = [
        path
        for path in MAPS_ROOT.rglob("*.txt")
        if path.is_file()
    ]
    return sorted(paths, key=map_sort_key)


def map_sort_key(path: Path) -> tuple[int, str, str]:
    try:
        relative = path.relative_to(MAPS_ROOT)
    except ValueError:
        return (len(LEVEL_ORDER), "", str(path))

    level = relative.parts[0] if len(relative.parts) > 1 else "other"
    return (
        LEVEL_ORDER.get(level, len(LEVEL_ORDER)),
        level,
        str(relative),
    )


def format_map_label(path: Path) -> str:
    relative = path.relative_to(MAPS_ROOT)
    level = relative.parts[0] if len(relative.parts) > 1 else "other"
    name = path.stem
    return f"{level:<10} - {name}"


def print_map_list(paths: list[Path]) -> None:
    print("Available maps:\n")
    for index, path in enumerate(paths, 1):
        print(f"[{index}] {format_map_label(path)}")


def choose_map_interactively(paths: list[Path]) -> Path:
    print_map_list(paths)
    print()

    while True:
        raw_choice = input("Choose a map number: ").strip()
        try:
            choice = int(raw_choice)
        except ValueError:
            print("Please enter a valid map number.")
            continue

        if 1 <= choice <= len(paths):
            return paths[choice - 1]

        print("Map number is outside the available range.")


def resolve_map_path(map_path: str | None) -> Path:
    if map_path is not None:
        return Path(map_path)

    paths = discover_maps()
    if not paths:
        raise SystemExit("No maps found under maps/maps_42.")

    return choose_map_interactively(paths)


def main() -> int:
    args = parse_args()

    if args.list_maps:
        paths = discover_maps()
        if not paths:
            print("No maps found under maps/maps_42.")
            return 1
        print_map_list(paths)
        return 0

    map_path = resolve_map_path(args.map_path)

    parser = MapParser()
    map_data = parser.parse_file(str(map_path))

    graph = Graph(map_data)
    path_finder = PathFinder(graph)
    max_paths = min(graph.get_nb_drones(), 10)
    path_results = path_finder.find_candidate_paths(max_paths=max_paths)

    simulator = Simulator(graph, path_results)
    turns = simulator.simulate()

    for turn in turns:
        print(turn)

    if args.visual:
        from src.display.pygame_renderer import (
            PygameRenderer,
            PygameUnavailableError,
        )

        try:
            renderer = PygameRenderer(map_data, turns)
            renderer.run()
        except PygameUnavailableError as exc:
            print(exc)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
