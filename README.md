*This project has been created as part of the 42 curriculum by lude-jes.*

# Fly-in

## Description

Fly-in is a Python project about routing a fleet of drones through a map made of
connected zones. The goal is to move all drones from the start hub to the end hub in
as few turns as possible, while respecting the rules of the map.

The program reads a map file, validates its format, builds a graph, finds useful
paths, assigns drones to those paths, and prints the simulation turn by turn.

The project handles:

- normal, priority, restricted, and blocked zones;
- maximum drone capacity inside zones;
- maximum link capacity between zones;
- turn-based drone movement;
- terminal output in the required `D<id>-<zone>` format;
- an optional pygame visualizer.

## Instructions

The project uses Python 3.10 or later.

Install the dependencies:

```sh
make install
```

Run the program with the interactive map selector:

```sh
make run
```

Run the program with the optional pygame visualizer:

```sh
make visual
```

List the available official maps:

```sh
python3 main.py --list-maps
```

Run a specific map directly:

```sh
python3 main.py maps/maps_42/easy/01_linear_path.txt
```

Run linting and type checks:

```sh
make lint
```

Run the benchmark tests:

```sh
make test
```

## Algorithm and Implementation Strategy

The map is parsed into object-oriented domain classes for zones, connections, and map
data. After parsing, the project builds an undirected graph using an adjacency list.
Blocked zones are ignored by pathfinding, while restricted zones have a higher movement
cost.

Pathfinding is based on Dijkstra's algorithm, implemented without external graph
libraries. Dijkstra is a good fit because the map has weighted movement costs:
normal and priority zones cost `1`, while restricted zones cost `2`.

To avoid sending all drones through only one shortest route, the project searches for
several candidate paths. After each path is found, penalties are added to its internal
zones. This encourages the next Dijkstra run to discover alternative routes when they
exist.

Drone assignment uses a score for each candidate path. The score considers:

- the path cost;
- how many drones were already assigned to that path;
- the lowest zone or link capacity on the path;
- a small bonus for priority zones.

The simulation then runs turn by turn. Each turn checks zone capacity, link capacity,
restricted-zone transit, and delivery status. A drone only moves when all constraints
allow it. The output is stored as one line per turn and printed at the end.

## Visual Representation

The optional visual mode uses pygame to replay the simulation after the terminal output
is produced.

It draws:

- the full map graph;
- connections between zones;
- colored zones for start, goal, priority, restricted, blocked, and normal zones;
- drone icons with their IDs;
- the current turn number.

This makes it easier to understand how drones spread across the graph, where congestion
happens, and how capacity rules affect the final result. It is optional and does not
replace the required terminal output.

## Verified Mandatory Benchmarks

These results were verified with:

```sh
make test
```

| Map | Turns | Target | Status |
| --- | ---: | ---: | --- |
| easy/01_linear_path | 4 | <= 6 | PASS |
| easy/02_simple_fork | 4 | <= 8 | PASS |
| easy/03_basic_capacity | 4 | <= 6 | PASS |
| medium/01_dead_end | 8 | <= 12 | PASS |
| medium/02_circular | 15 | <= 15 | PASS |
| medium/03_priority | 7 | <= 12 | PASS |
| hard/01_maze_nightmare | 13 | <= 30 | PASS |
| hard/02_capacity_hell | 16 | <= 35 | PASS |
| hard/03_ultimate | 27 | <= 45 | PASS |

Mandatory maps passed: `9/9`.

## Resources

General references used for this project:

- Dijkstra's shortest path algorithm;
- graph representation with adjacency lists;
- priority queues with Python `heapq`;
- turn-based simulation;
- Python dataclasses;
- Python type hints and mypy;
- flake8 and PEP 8 style rules;
- pygame documentation for the optional visualizer.

### AI Usage

AI was used as a support tool for documentation help and README drafting, as well as tests elaboration. 
It was not used as a replacement for understanding the project logic. The code, algorithm choices,
testing, and final behavior remain the responsibility of the student.

## Tests

The `tests/` directory contains development tests and benchmark runners used to check
the parser, pathfinding, simulator, and final mandatory map performance. These tests are
useful for validation, even if they are not part of the graded submission.
