from src.domain.drone import Drone
from src.graph.graph import Graph
from src.simulation.simulator_error import SimulatorError


class Simulator:
    def __init__(
            self, graph: Graph, paths: list[list[str]]
    ) -> None:
        self.graph = graph
        self.paths = paths
        self.nb_drones = self.graph.get_nb_drones()

    def _create_drones(self) -> list[Drone]:
        if not self.paths:
            raise SimulatorError(
                "Cannot simulate without paths"
            )

        drones: list[Drone] = []

        for drone_id in range(1, self.nb_drones + 1):
            path = self.paths[(drone_id - 1) % len(self.paths)]
            drone = Drone(drone_id, path)
            drones.append(drone)

        return drones

    def _get_zone_occupancy(self, drones: list[Drone]) -> dict[str, int]:
        occupancy: dict[str, int] = {}

        for drone in drones:
            if drone.is_delivered():
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
            occupancy: dict[str, int]
    ) -> str | None:
        target = drone.next_zone()
        curr = drone.current_zone()
        end = self.graph.get_start_end()[1]

        if target is None:
            return None

        if not self._has_zone_capacity(target, occupancy):
            return None

        occupancy[curr] -= 1

        if target != end:
            occupancy[target] = occupancy.get(target, 0) + 1

        drone.move()

        return f"D{drone.id}-{target}"

    def _run_turn(self, drones: list[Drone]) -> str:
        occupancy = self._get_zone_occupancy(drones)
        movements: list[str] = []

        for drone in drones:
            if drone.is_delivered():
                continue
            mov_str = self._try_move_drone(drone, occupancy)
            if mov_str is not None:
                movements.append(mov_str)

        return " ".join(movements)

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
