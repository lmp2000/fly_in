import pytest

from src.domain.zone import ZoneType
from src.parser.map_parser import MapParser
from src.parser.parse_error import ParseError


def parse_map(text: str):
    parser = MapParser()
    return parser.parse_lines(text.strip("\n").splitlines())


def assert_parse_error(text: str, message: str) -> ParseError:
    with pytest.raises(ParseError) as exc_info:
        parse_map(text)
    assert message in exc_info.value.message
    return exc_info.value


def test_valid_minimal_map():
    map_data = parse_map(
        """
nb_drones: 1
start_hub: start 0 0
end_hub: end 1 0
connection: start-end
"""
    )

    assert map_data.nb_drones == 1
    assert map_data.start_name == "start"
    assert map_data.end_name == "end"
    assert len(map_data.zones) == 2
    assert len(map_data.connections) == 1


def test_valid_comments_and_blank_lines():
    map_data = parse_map(
        """
# ignored comment

nb_drones: 2

start_hub: start 0 0

# another ignored comment
end_hub: end 1 0 # inline comment
connection: start-end
"""
    )

    assert map_data.nb_drones == 2
    assert list(map_data.zones) == ["start", "end"]
    assert len(map_data.connections) == 1


def test_valid_metadata_in_different_orders():
    map_data = parse_map(
        """
nb_drones: 3
start_hub: start 0 0 [max_drones=2 color=red zone=priority]
end_hub: end 1 0 [color=blue zone=normal max_drones=4]
connection: start-end [max_link_capacity=2]
"""
    )

    assert map_data.zones["start"].zone_type == ZoneType.PRIORITY
    assert map_data.zones["start"].color == "red"
    assert map_data.zones["start"].max_drones == 2
    assert map_data.zones["end"].zone_type == ZoneType.NORMAL
    assert map_data.zones["end"].color == "blue"
    assert map_data.zones["end"].max_drones == 4
    assert map_data.connections[0].max_link_capacity == 2


def test_valid_arbitrary_single_word_colors():
    map_data = parse_map(
        """
nb_drones: 1
start_hub: start 0 0 [color=chartreuse]
end_hub: end 1 0 [color=brand_42]
connection: start-end
"""
    )

    assert map_data.zones["start"].color == "chartreuse"
    assert map_data.zones["end"].color == "brand_42"


def test_valid_negative_coordinates_preserve_existing_behavior():
    map_data = parse_map(
        """
nb_drones: 1
start_hub: start -1 0
end_hub: end 1 -2
connection: start-end
"""
    )

    assert map_data.zones["start"].x == -1
    assert map_data.zones["end"].y == -2


def test_reject_self_connection():
    error = assert_parse_error(
        """
nb_drones: 1
start_hub: start 0 0
end_hub: end 1 0
connection: start-start
""",
        "Self-connection is not allowed",
    )

    assert error.line_number == 4


def test_reject_underscore_nb_drones():
    error = assert_parse_error(
        """
nb_drones: 1_000
start_hub: start 0 0
end_hub: end 1 0
connection: start-end
""",
        "Number of drones must be a positive integer",
    )

    assert error.line_number == 1


def test_reject_underscore_coordinates():
    error = assert_parse_error(
        """
nb_drones: 1
start_hub: start 0 0
end_hub: end 1_000 0
connection: start-end
""",
        "Coordinates must be valid integers",
    )

    assert error.line_number == 3


def test_reject_underscore_max_drones():
    error = assert_parse_error(
        """
nb_drones: 1
start_hub: start 0 0 [max_drones=1_000]
end_hub: end 1 0
connection: start-end
""",
        "Max drones must be a positive integer",
    )

    assert error.line_number == 2


def test_reject_underscore_max_link_capacity():
    error = assert_parse_error(
        """
nb_drones: 1
start_hub: start 0 0
end_hub: end 1 0
connection: start-end [max_link_capacity=1_000]
""",
        "Max link capacity must be a positive integer",
    )

    assert error.line_number == 4


def test_reject_duplicate_nb_drones_with_specific_error():
    error = assert_parse_error(
        """
nb_drones: 1
nb_drones: 2
start_hub: start 0 0
end_hub: end 1 0
connection: start-end
""",
        "Duplicate nb_drones declaration",
    )

    assert error.line_number == 2


def test_reject_missing_start_hub_with_specific_error():
    error = assert_parse_error(
        """
nb_drones: 1
end_hub: end 1 0
hub: mid 0 0
connection: mid-end
""",
        "Missing required start_hub declaration",
    )

    assert error.line_number == 4


def test_reject_missing_end_hub_with_specific_error():
    error = assert_parse_error(
        """
nb_drones: 1
start_hub: start 0 0
hub: mid 1 0
connection: start-mid
""",
        "Missing required end_hub declaration",
    )

    assert error.line_number == 4


def test_reject_malformed_prefix_like_double_colon():
    error = assert_parse_error(
        """
nb_drones: 1
start_hub: start 0 0
hub:: bad 1 0
end_hub: end 2 0
connection: start-end
""",
        "Malformed line prefix",
    )

    assert error.line_number == 3
