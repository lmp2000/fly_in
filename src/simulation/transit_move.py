from dataclasses import dataclass


@dataclass
class TransitMove:
    drone_id: int
    from_zone: str
    to_zone: str
    connection_key: tuple[str, str]
    remaining_turns: int