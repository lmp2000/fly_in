"""Manual runner for Phase 6 optimized simulation."""

from dataclasses import dataclass

from src.graph.graph import Graph
from src.parser.map_parser import MapParser
from src.pathfinding.path_finder import PathFinder
from src.pathfinding.path_result import PathResult
from src.simulation.simulator import Simulator

DEBUG_OUTPUT = False


@dataclass(frozen=True)
class BenchmarkCase:
    name: str
    path: str
    target_turns: int
    mandatory: bool = True
    strict_target: bool = False


@dataclass(frozen=True)
class BenchmarkResult:
    case: BenchmarkCase
    path_results: list[PathResult]
    turns: list[str]
    passed: bool


BENCHMARK_CASES = [
    BenchmarkCase(
        "easy/01_linear_path",
        "maps/maps_42/easy/01_linear_path.txt",
        6,
    ),
    BenchmarkCase(
        "easy/02_simple_fork",
        "maps/maps_42/easy/02_simple_fork.txt",
        8,
    ),
    BenchmarkCase(
        "easy/03_basic_capacity",
        "maps/maps_42/easy/03_basic_capacity.txt",
        6,
    ),
    BenchmarkCase(
        "medium/01_dead_end",
        "maps/maps_42/medium/01_dead_end_trap.txt",
        12,
    ),
    BenchmarkCase(
        "medium/02_circular",
        "maps/maps_42/medium/02_circular_loop.txt",
        15,
    ),
    BenchmarkCase(
        "medium/03_priority",
        "maps/maps_42/medium/03_priority_puzzle.txt",
        12,
    ),
    BenchmarkCase(
        "hard/01_maze_nightmare",
        "maps/maps_42/hard/01_maze_nightmare.txt",
        30,
    ),
    BenchmarkCase(
        "hard/02_capacity_hell",
        "maps/maps_42/hard/02_capacity_hell.txt",
        35,
    ),
    BenchmarkCase(
        "hard/03_ultimate",
        "maps/maps_42/hard/03_ultimate_challenge.txt",
        45,
    ),
    BenchmarkCase(
        "challenger/01_the_impossible_dream",
        "maps/maps_42/challenger/01_the_impossible_dream.txt",
        45,
        mandatory=False,
        strict_target=True,
    ),
]


def target_label(case: BenchmarkCase) -> str:
    """Return the printable target comparison for a benchmark."""
    if case.strict_target:
        return f"< {case.target_turns}"
    return f"<= {case.target_turns}"


def is_passing(case: BenchmarkCase, total_turns: int) -> bool:
    """Check benchmark status for mandatory and optional cases."""
    if case.strict_target:
        return total_turns < case.target_turns
    return total_turns <= case.target_turns


def diagnose_failure(
        path_results: list[PathResult],
        total_turns: int,
        target_turns: int,
) -> str:
    """Return a short, heuristic diagnosis for a failed benchmark."""
    if len(path_results) <= 1:
        return "path discovery: only one usable path was discovered."

    shared_zone_counts: dict[str, int] = {}
    for result in path_results:
        for zone in result.zones[1:-1]:
            shared_zone_counts[zone] = shared_zone_counts.get(zone, 0) + 1

    shared_zones = [
        zone for zone, count in shared_zone_counts.items()
        if count > 1
    ]
    if shared_zones and total_turns > target_turns:
        return (
            "path assignment: discovered paths share bottleneck zones, "
            "so drones may still be routed into congestion."
        )

    return (
        "turn scheduling: paths look available, but capacity or restricted "
        "transit timing appears to delay delivery."
    )


def run_case(case: BenchmarkCase) -> BenchmarkResult:
    """Run one official benchmark map."""
    parser = MapParser()
    map_data = parser.parse_file(case.path)

    graph = Graph(map_data)
    path_finder = PathFinder(graph)
    max_paths = min(graph.get_nb_drones(), 10)
    path_results = path_finder.find_candidate_paths(max_paths=max_paths)

    simulator = Simulator(graph, path_results)
    turns = simulator.simulate()
    passed = is_passing(case, len(turns))

    return BenchmarkResult(case, path_results, turns, passed)


def print_case_result(result: BenchmarkResult) -> None:
    """Print detailed output for one benchmark result."""
    case = result.case
    total_turns = len(result.turns)
    status = "PASS" if result.passed else "FAIL"

    print(f"\n== {case.name} ==")
    print("Discovered paths:")
    for path_result in result.path_results:
        print(f"  {path_result.zones} | cost={path_result.cost}")

    print(f"Total turns: {total_turns}")
    print(f"Target turns: {target_label(case)}")
    print(f"Status: {status}")

    if result.passed and not DEBUG_OUTPUT:
        return

    print("\nSimulation output:")
    for turn in result.turns:
        print(turn)

    if not result.passed:
        diagnosis = diagnose_failure(
            result.path_results,
            total_turns,
            case.target_turns,
        )
        print(f"\nDiagnosis: {diagnosis}")


def print_summary(results: list[BenchmarkResult]) -> None:
    """Print the benchmark summary table."""
    print("\nSummary")
    print("Map | Turns | Target | Status")
    print("--- | --- | --- | ---")

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(
            f"{result.case.name} | {len(result.turns)} | "
            f"{target_label(result.case)} | {status}"
        )

    mandatory_results = [
        result for result in results
        if result.case.mandatory
    ]
    mandatory_passed = sum(
        1 for result in mandatory_results
        if result.passed
    )

    print(
        f"\nMandatory passed: {mandatory_passed}/"
        f"{len(mandatory_results)}"
    )

    optional_results = [
        result for result in results
        if not result.case.mandatory
    ]
    for result in optional_results:
        status = "PASS" if result.passed else "FAIL"
        print(
            f"Optional challenger: {status} "
            f"({len(result.turns)} turns, target {target_label(result.case)})"
        )


def main() -> None:
    """Run official Phase 6 benchmark maps."""
    results: list[BenchmarkResult] = []

    for case in BENCHMARK_CASES:
        result = run_case(case)
        print_case_result(result)
        results.append(result)

    print_summary(results)


if __name__ == "__main__":
    main()
