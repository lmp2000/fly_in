from dataclasses import dataclass


@dataclass
class Connection:
    zone_a: str
    zone_b: str
    max_link_capacity: int = 1

    def key(self) -> tuple[str, str]:
        return tuple(sorted((self.zone_a, self.zone_b)))

