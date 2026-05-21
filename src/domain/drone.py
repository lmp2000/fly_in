from dataclasses import dataclass


class DroneError(Exception):
    """Raised when a drone cannot be created or advanced safely."""

    pass


@dataclass
class Drone:
    """Track one drone's assigned path and current position.

    Attributes:
        id: One-based drone identifier used in output.
        path: Ordered zone names assigned to the drone.
        path_index: Current index within the path.
    """

    id: int
    path: list[str]
    path_index: int = 0

    def __post_init__(self) -> None:
        """Validate that the drone has at least one zone in its path.

        Raises:
            DroneError: If the path is empty.
        """
        if not self.path:
            raise DroneError(
                "Drone path cannot be empty."
            )

    def current_zone(self) -> str:
        """Return the zone where the drone is currently located.

        Returns:
            The current zone name.
        """
        return self.path[self.path_index]

    def next_zone(self) -> str | None:
        """Return the next zone in the assigned path, if any.

        Returns:
            The next zone name, or None when the drone is delivered.
        """
        if len(self.path) > self.path_index + 1:
            return self.path[self.path_index + 1]
        return None

    def is_delivered(self) -> bool:
        """Return whether the drone has reached the final zone.

        Returns:
            True when the drone is at the end of its path.
        """
        return self.path_index == len(self.path) - 1

    def move(self) -> None:
        """Advance the drone by one path step when possible."""
        if self.next_zone() is not None:
            self.path_index += 1
