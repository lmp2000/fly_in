from src.domain.drone import Drone
from src.graph.graph import Graph
from src.domain.zone import ZoneType
from src.simulation.simulator_error import SimulatorError
from src.simulation.transit_move import TransitMove
from src.domain.connection import Connection
from src.simulation.path_assigner import PathAssigner
from src.pathfinding.path_result import PathResult


class Simulator:
    def __init__(
            self, graph: Graph, paths: list[PathResult],
    ) -> None:
        self.graph = graph
        self.paths = paths
        self.nb_drones = self.graph.get_nb_drones()
        self.active_transits: list[TransitMove] = []

    def _create_drones(self) -> list[Drone]:
        if not self.paths:
            raise SimulatorError(
                "Cannot simulate without paths"
            )

        drones: list[Drone] = []
        assigner = PathAssigner(self.graph, self.paths)
        assigned_paths = assigner.assign()

        for drone_id in range(1, self.nb_drones + 1):
            path = assigned_paths[drone_id - 1]
            drone = Drone(drone_id, path)
            drones.append(drone)

        return drones

    def _get_zone_occupancy(self, drones: list[Drone]) -> dict[str, int]:
        occupancy: dict[str, int] = {}

        for drone in drones:
            if drone.is_delivered():
                continue

            if self._get_transit(drone):
                continue

            zone = drone.current_zone()
            occupancy[zone] = occupancy.get(zone, 0) + 1

        return occupancy

    def _has_zone_capacity(
            self,
            zone_name: str,
            occupancy: dict[str, int]
    ) -> bool:
        if zone_name == self.graph.get_start_end()[1]:
            return True
        limit = self.graph.get_zone(zone_name).max_drones
        curr = occupancy.get(zone_name, 0)
        return curr < limit

    def _try_move_drone(
            self,
            drone: Drone,
            occupancy: dict[str, int],
            used_connections: dict[tuple[str, str], int]
    ) -> str | None:
        target = drone.next_zone()

        if target is None:
            return None

        curr = drone.current_zone()
        end = self.graph.get_start_end()[1]

        connection = self.graph.get_connection(curr, target)

        if not self._has_zone_capacity(target, occupancy):
            return None

        if not self._has_connection_capacity(connection, used_connections):
            return None

        occupancy[curr] -= 1
        used_connections[connection.key()] = used_connections.get(connection.key(), 0) + 1

        if self.graph.get_zone(target).zone_type == ZoneType.RESTRICTED:
            if target != end:
                occupancy[target] = occupancy.get(target, 0) + 1

            c_key = connection.key()
            transit = TransitMove(drone.id, curr, target, c_key, 1)
            self.active_transits.append(transit)
            return f"D{drone.id}-{c_key[0]}-{c_key[1]}"

        if target != end:
            occupancy[target] = occupancy.get(target, 0) + 1

        drone.move()

        return f"D{drone.id}-{target}"

    def _run_turn(self, drones: list[Drone]) -> str:
        moved_drones: set[int] = set()
        movements: list[str] = self._process_transits(drones, moved_drones)
        occupancy: dict[str, int] = self._get_zone_occupancy(drones)
        used_connections: dict[tuple[str, str], int] = self._get_active_connections()

        for drone in self._get_move_order(drones):
            if drone.is_delivered():
                continue

            if self._get_transit(drone):
                continue

            if drone.id in moved_drones:
                continue

            mov_str = self._try_move_drone(drone, occupancy, used_connections)
            if mov_str is not None:
                movements.append(mov_str)

        return " ".join(movements)

    def _get_transit(self, drone: Drone) -> TransitMove | None:
        lookup_id = drone.id
        for t in self.active_transits:
            if lookup_id == t.drone_id:
                return t
        return None

    def _process_transits(self, drones: list[Drone], moved_drones: set[int]) -> list[str]:
        movements: list[str] = []
        remaining_transits: list[TransitMove] = []

        for transit in self.active_transits:
            transit.remaining_turns -= 1

            if transit.remaining_turns == 0:
                drone = next(
                    drone for drone in drones if drone.id == transit.drone_id
                )
                drone.move()
                moved_drones.add(drone.id)
                mov_str = f"D{drone.id}-{transit.to_zone}"
                movements.append(mov_str)
            else:
                remaining_transits.append(transit)

        self.active_transits = remaining_transits
        return movements

    def _has_connection_capacity(
            self,
            connection: Connection,
            used_connections: dict[tuple[str, str], int],
    ) -> bool:
        key = connection.key()
        used = used_connections.get(key, 0)
        return used < connection.max_link_capacity

    def _get_active_connections(self) -> dict[tuple[str, str], int]:
        active_connections: dict[tuple[str, str], int] = {}
        for transit in self.active_transits:
            active_connections[transit.connection_key] = active_connections.get(
                transit.connection_key, 0
            ) + 1
        return active_connections

    def _get_move_order(self, drones: list[Drone]) -> list[Drone]:
        return sorted(
            drones, key=lambda d: d.path_index, reverse=True
        )

    def simulate(self) -> list[str]:
        drones = self._create_drones()
        turns: list[str] = []
        max_retries = 500

        while not all(d.is_delivered() for d in drones):
            turn = self._run_turn(drones)
            if turn:
                turns.append(turn)
            else:
                max_retries -= 1
                if max_retries == 0:
                    raise SimulatorError(
                        "Infinite loop danger"
                    )

        return turns
