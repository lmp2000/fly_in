from src.domain.map_data import MapData
from src.domain.zone import Zone, ZoneType
from src.domain.connection import Connection
from src.parser.parse_error import ParseError
from src.parser.metadata_parser import parse_metadata


class MapParser:
    def parse_file(self, file_path: str) -> MapData:
        buffer: list[str] = []
        with open(file_path, "r") as f:
            for line in f:
                buffer.append(line)
        return self.parse_lines(buffer)

    def parse_lines(self, lines: list[str]) -> MapData:
        clean_lines: list[tuple[int, str]] = []

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                continue
            clean_lines.append((i, line))

        if not clean_lines:
            raise ParseError(0, "Error parsing lines from file")

        if not clean_lines[0][1].startswith('nb_drones:'):
            raise ParseError(
                clean_lines[0][0], "First line must start with 'nb_drones:'"
            )

        nb_drones = self.parse_nbdrones(clean_lines)
        zones: dict[str, Zone] = {}
        connections: list[Connection] = []
        start_hub: str | None = None
        end_hub: str | None = None

        for line in clean_lines[1:]:
            if line[1].startswith('hub:'):
                zone = self.parse_zone(line[0], line[1].split(':', 1)[1].strip())
                if zone.name in zones:
                    raise ParseError(
                        line[0], "Duplicate zone name"
                    )
                zones[zone.name] = zone
            elif line[1].startswith('start_hub:'):
                if start_hub is not None:
                    raise ParseError(
                        line[0], 'There can only be one start_hub'
                    )
                start_zone = self.parse_zone(line[0], line[1].split(':', 1)[1].strip())
                start_hub = start_zone.name
                if start_hub in zones:
                    raise ParseError(
                        line[0], "Duplicate zone name"
                    )
                zones[start_hub] = start_zone
            elif line[1].startswith('end_hub:'):
                if end_hub is not None:
                    raise ParseError(
                        line[0], 'There can only be one end_hub'
                    )
                end_zone = self.parse_zone(line[0], line[1].split(':', 1)[1].strip())
                end_hub = end_zone.name
                if end_hub in zones:
                    raise ParseError(
                        line[0], "Duplicate zone name"
                    )
                zones[end_hub] = end_zone
            elif line[1].startswith('connection:'):
                connection = self.parse_connection(line[0], line[1].split(':', 1)[1].strip())
                if connection.zone_a not in zones:
                    raise ParseError(
                        line[0], f"Unknown zone in {connection.zone_a}"
                    )
                if connection.zone_b not in zones:
                    raise ParseError(
                        line[0], f"Unknown zone in {connection.zone_b}"
                    )
                if connection.key() in [c.key() for c in connections]:
                    raise ParseError(
                        line[0], "Duplicate connections are not allowed"
                    )
                connections.append(connection)
            else:
                raise ParseError(
                    line[0], "Unknown line type"
                )

        if start_hub is None or end_hub is None:
            raise ParseError(
                0, "Map data must contain a start hub and an end hub"
            )

        return MapData(nb_drones, zones, connections, start_hub, end_hub)

    def parse_nbdrones(self, clean_lines: list[tuple[int, str]]) -> int:
        value = clean_lines[0][1].split(':', 1)[1].strip()

        try:
            nb_drones = int(value)
        except ValueError:
            raise ParseError(
                clean_lines[0][0], "Error parsing number of drones"
            )

        if nb_drones <= 0:
            raise ParseError(
                clean_lines[0][0], "Number of drones must be a positive number"
            )

        return nb_drones

    def parse_zone(self, line_number: int, zone_line: str) -> Zone:
        components = zone_line.split()

        if len(components) < 3:
            raise ParseError(
                line_number, "Invalid zone data"
            )

        name, x_text, y_text, *extra = components

        if '-' in name or ' ' in name:
            raise ParseError(
                line_number, 'Invalid zone name - cannot contain "-" or spaces'
            )
        try:
            x = int(x_text)
            y = int(y_text)
        except ValueError:
            raise ParseError(
                line_number, "Coordinates must be valid integers"
            )

        zone = Zone(
            name,
            x,
            y,
        )

        if not extra:
            return zone

        metadata_text = " ".join(extra)
        metadata = parse_metadata(metadata_text, line_number)

        zone_type, color, max_drones = None, None, None

        for key, value in metadata.items():
            if key == 'zone':
                try:
                    zone_type = ZoneType(value)
                except ValueError:
                    raise ParseError(
                        line_number, "Invalid zone type"
                    )
            elif key == 'color':
                color = value
            elif key == 'max_drones':
                max_drones_text = value
                try:
                    max_drones = int(max_drones_text)
                except ValueError:
                    raise ParseError(
                        line_number, "Max drones must be a positive integer"
                    )
                if max_drones < 1:
                    raise ParseError(
                        line_number, "Max drones must be a positive integer"
                    )
            else:
                raise ParseError(
                    line_number, "Invalid zone metadata"
                )

        if zone_type:
            zone.zone_type = zone_type
        if color:
            zone.color = color
        if max_drones:
            zone.max_drones = max_drones
        return zone

    def parse_connection(self, line_number: int, line: str) -> Connection:
        if '-' not in line:
            raise ParseError(
                line_number, "Invalid connection, must use '-'"
            )
        components = line.split()

        if len(components) > 2:
            raise ParseError(
                line_number, "Invalid connection data"
            )

        zones = components[0].split('-')
        if len(zones) != 2:
            raise ParseError(
                line_number, "Invalid connection data"
            )
        a = zones[0]
        if not a:
            raise ParseError(
                line_number, "Invalid zone a"
            )
        b = zones[1]
        if not b:
            raise ParseError(
                line_number, "Invalid zone b"
            )

        connection = Connection(a, b)

        if len(components) < 2:
            return connection

        metadata = parse_metadata(components[1], line_number)

        for key, value in metadata.items():
            if key == 'max_link_capacity':
                try:
                    capacity = int(value)
                except ValueError:
                    raise ParseError(
                        line_number, "Max link capacity must be an integer"
                    )
                if capacity < 1:
                    raise ParseError(
                        line_number, "Max link capacity must be bigger than 0"
                    )
                connection.max_link_capacity = capacity
            else:
                raise ParseError(
                    line_number, "Invalid connection metadata"
                )

        return connection