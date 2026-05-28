from src.domain.map_data import MapData
from src.domain.zone import Zone, ZoneType
from src.domain.connection import Connection
from src.parser.parse_error import ParseError
from src.parser.metadata_parser import parse_metadata


def parse_positive_integer(
    value: str,
    line_number: int,
    error_message: str,
) -> int:
    """Parse a digits-only positive integer token."""
    if not value.isdigit():
        raise ParseError(line_number, error_message)

    parsed_value = int(value)
    if parsed_value < 1:
        raise ParseError(line_number, error_message)
    return parsed_value


def parse_integer(value: str, line_number: int, error_message: str) -> int:
    """Parse a strict integer token, allowing a leading minus sign."""
    if value.startswith("-"):
        digits = value[1:]
    else:
        digits = value

    if not digits or not digits.isdigit():
        raise ParseError(line_number, error_message)
    return int(value)


class MapParser:
    """Parse Fly-in map files into validated domain objects."""

    def parse_file(self, file_path: str) -> MapData:
        """Parse a map file into validated map data.

        Args:
            file_path: Path to the map file.

        Returns:
            A validated MapData instance.

        Raises:
            ParseError: If the file contents do not follow the map format.
        """
        buffer: list[str] = []
        with open(file_path, "r") as f:
            for line in f:
                buffer.append(line)
        return self.parse_lines(buffer)

    def parse_lines(self, lines: list[str]) -> MapData:
        """Parse raw map lines into validated map data.

        Args:
            lines: Raw lines from a map file.

        Returns:
            A validated MapData instance.

        Raises:
            ParseError: If required sections or declarations are invalid.
        """
        clean_lines: list[tuple[int, str]] = []

        for i, line in enumerate(lines, 1):
            line = line.split('#', 1)[0].strip()
            if not line:
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

        for line_number, line in clean_lines[1:]:
            if line.startswith('nb_drones:'):
                raise ParseError(
                    line_number, "Duplicate nb_drones declaration"
                )
            if line.startswith(('hub::', 'start_hub::', 'end_hub::')):
                raise ParseError(
                    line_number, "Malformed line prefix"
                )
            if line.startswith('hub:'):
                zone = self.parse_zone(
                    line_number, line.split(':', 1)[1].strip()
                )
                if zone.name in zones:
                    raise ParseError(
                        line_number, "Duplicate zone name"
                    )
                zones[zone.name] = zone
            elif line.startswith('start_hub:'):
                if start_hub is not None:
                    raise ParseError(
                        line_number, 'There can only be one start_hub'
                    )
                start_zone = self.parse_zone(
                    line_number, line.split(':', 1)[1].strip()
                )
                start_hub = start_zone.name
                if start_hub in zones:
                    raise ParseError(
                        line_number, "Duplicate zone name"
                    )
                zones[start_hub] = start_zone
            elif line.startswith('end_hub:'):
                if end_hub is not None:
                    raise ParseError(
                        line_number, 'There can only be one end_hub'
                    )
                end_zone = self.parse_zone(
                    line_number, line.split(':', 1)[1].strip()
                )
                end_hub = end_zone.name
                if end_hub in zones:
                    raise ParseError(
                        line_number, "Duplicate zone name"
                    )
                zones[end_hub] = end_zone
            elif line.startswith('connection:'):
                connection = self.parse_connection(
                    line_number, line.split(':', 1)[1].strip()
                )
                if connection.zone_a not in zones:
                    raise ParseError(
                        line_number, f"Unknown zone in {connection.zone_a}"
                    )
                if connection.zone_b not in zones:
                    raise ParseError(
                        line_number, f"Unknown zone in {connection.zone_b}"
                    )
                if connection.key() in [c.key() for c in connections]:
                    raise ParseError(
                        line_number, "Duplicate connections are not allowed"
                    )
                connections.append(connection)
            else:
                raise ParseError(
                    line_number, "Unknown line type"
                )

        if start_hub is None or end_hub is None:
            missing = []
            if start_hub is None:
                missing.append("start_hub")
            if end_hub is None:
                missing.append("end_hub")
            raise ParseError(
                clean_lines[-1][0],
                f"Missing required {' and '.join(missing)} declaration",
            )

        return MapData(nb_drones, zones, connections, start_hub, end_hub)

    def parse_nbdrones(self, clean_lines: list[tuple[int, str]]) -> int:
        """Parse the drone count declaration.

        Args:
            clean_lines: Non-empty cleaned map lines with original numbers.

        Returns:
            The positive number of drones declared by the map.

        Raises:
            ParseError: If the drone count is missing or invalid.
        """
        value = clean_lines[0][1].split(':', 1)[1].strip()

        return parse_positive_integer(
            value,
            clean_lines[0][0],
            "Number of drones must be a positive integer",
        )

    def parse_zone(self, line_number: int, zone_line: str) -> Zone:
        """Parse a zone declaration.

        Args:
            line_number: Source line number used for error reporting.
            zone_line: Zone declaration without the leading field name.

        Returns:
            The parsed Zone object.

        Raises:
            ParseError: If the zone name, coordinates, or metadata is invalid.
        """
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
        x = parse_integer(
            x_text, line_number, "Coordinates must be valid integers"
        )
        y = parse_integer(
            y_text, line_number, "Coordinates must be valid integers"
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
                max_drones = parse_positive_integer(
                    max_drones_text,
                    line_number,
                    "Max drones must be a positive integer",
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
        """Parse a connection declaration.

        Args:
            line_number: Source line number used for error reporting.
            line: Connection declaration without the leading field name.

        Returns:
            The parsed Connection object.

        Raises:
            ParseError: If endpoints or connection metadata are invalid.
        """
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
        if a == b:
            raise ParseError(
                line_number, "Self-connection is not allowed"
            )

        connection = Connection(a, b)

        if len(components) < 2:
            return connection

        metadata = parse_metadata(components[1], line_number)

        for key, value in metadata.items():
            if key == 'max_link_capacity':
                capacity = parse_positive_integer(
                    value,
                    line_number,
                    "Max link capacity must be a positive integer",
                )
                connection.max_link_capacity = capacity
            else:
                raise ParseError(
                    line_number, "Invalid connection metadata"
                )

        return connection
