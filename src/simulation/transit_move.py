from dataclasses import dataclass


@dataclass
class TransitMove:
    """Track a drone moving through a restricted connection.

    Attributes:
        drone_id: Identifier of the drone in transit.
        from_zone: Zone where the transit started.
        to_zone: Zone where the transit ends.
        connection_key: Stable key for the occupied connection.
        remaining_turns: Turns remaining before arrival.
    """

    drone_id: int
    from_zone: str
    to_zone: str
    connection_key: tuple[str, str]
    remaining_turns: int
