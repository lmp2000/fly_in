from dataclasses import dataclass


class DroneError(Exception):
    pass


@dataclass
class Drone:
    id: int
    path: list[str]
    path_index: int = 0

    def __post_init__(self) -> None:
        if not self.path:
            raise DroneError(
                "Drone path cannot be empty."
            )

    def current_zone(self) -> str:
        return self.path[self.path_index]

    def next_zone(self) -> str | None:
        if len(self.path) > self.path_index + 1:
            return self.path[self.path_index + 1]
        return None

    def is_delivered(self) -> bool:
        return self.path_index == len(self.path) - 1

    def move(self) -> None:
        if self.next_zone() is not None:
            self.path_index += 1