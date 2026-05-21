from pathlib import Path
from typing import Any

from src.domain.map_data import MapData
from src.domain.zone import ZoneType


PYGAME_INSTALL_MESSAGE = (
    "Visual renderer requires pygame. Install it with: "
    "python3 -m pip install pygame"
)

BACKGROUND_COLOR = (245, 247, 250)
CONNECTION_COLOR = (90, 100, 120)
TEXT_COLOR = (20, 25, 35)
ZONE_RADIUS = 24
ZONE_BORDER_COLOR = (35, 42, 55)
START_COLOR = (76, 175, 80)
END_COLOR = (245, 190, 65)
NORMAL_COLOR = (190, 205, 220)
PRIORITY_COLOR = (74, 170, 220)
RESTRICTED_COLOR = (225, 110, 70)
BLOCKED_COLOR = (85, 90, 100)


class PygameUnavailableError(RuntimeError):
    """Raised when pygame is required but not installed."""

    pass


class PygameRenderer:
    """Replay simulation turns in a pygame window."""

    def __init__(
            self,
            map_data: MapData,
            turns: list[str],
            width: int = 1000,
            height: int = 700,
            turn_delay_ms: int = 800,
    ) -> None:
        """Create a pygame renderer for a completed simulation.

        Args:
            map_data: Parsed map definition to draw.
            turns: Simulation output lines to replay.
            width: Window width in pixels.
            height: Window height in pixels.
            turn_delay_ms: Delay between rendered turns.

        Raises:
            PygameUnavailableError: If pygame is not installed.
        """
        try:
            import pygame
        except ModuleNotFoundError as exc:
            raise PygameUnavailableError(PYGAME_INSTALL_MESSAGE) from exc

        self.pygame: Any = pygame
        self.map_data = map_data
        self.turns = turns
        self.width = width
        self.height = height
        self.turn_delay_ms = turn_delay_ms
        self.padding = 80
        self.positions: dict[int, str] = {
            drone_id: map_data.start_name
            for drone_id in range(1, map_data.nb_drones + 1)
        }
        self.zone_positions = self._scale_zone_positions()

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-in Visualizer")
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.clock = pygame.time.Clock()

        project_root = Path(__file__).resolve().parents[2]
        assets_dir = project_root / "assets"
        self.drone_image = pygame.transform.smoothscale(
            pygame.image.load(assets_dir / "drone.png").convert_alpha(),
            (28, 27),
        )

    def run(self) -> None:
        """Open the renderer window and replay all simulation turns."""
        current_turn = 0
        if not self._draw_and_wait(current_turn):
            self.pygame.quit()
            return

        for turn_number, turn in enumerate(self.turns, 1):
            self._apply_turn(turn)
            current_turn = turn_number
            if not self._draw_and_wait(current_turn):
                self.pygame.quit()
                return

        self._wait_until_closed(current_turn)
        self.pygame.quit()

    def _scale_zone_positions(self) -> dict[str, tuple[int, int]]:
        """Scale map coordinates into screen positions."""
        zones = list(self.map_data.zones.values())
        min_x = min(zone.x for zone in zones)
        max_x = max(zone.x for zone in zones)
        min_y = min(zone.y for zone in zones)
        max_y = max(zone.y for zone in zones)
        x_range = max_x - min_x
        y_range = max_y - min_y
        usable_width = self.width - (self.padding * 2)
        usable_height = self.height - (self.padding * 2)

        positions: dict[str, tuple[int, int]] = {}
        for zone in zones:
            if x_range == 0:
                screen_x = self.width // 2
            else:
                screen_x = int(
                    self.padding
                    + ((zone.x - min_x) / x_range) * usable_width
                )

            if y_range == 0:
                screen_y = self.height // 2
            else:
                screen_y = int(
                    self.padding
                    + ((max_y - zone.y) / y_range) * usable_height
                )

            positions[zone.name] = (screen_x, screen_y)

        return positions

    def _apply_turn(self, turn: str) -> None:
        """Apply one textual simulation turn to drone positions."""
        for token in turn.split():
            parts = token.split("-")
            if len(parts) < 2 or not parts[0].startswith("D"):
                continue

            try:
                drone_id = int(parts[0][1:])
            except ValueError:
                continue

            if drone_id not in self.positions:
                continue

            self.positions[drone_id] = parts[-1]

    def _draw_and_wait(self, current_turn: int) -> bool:
        """Draw the current state and wait for the turn delay."""
        self._draw(current_turn)
        return self._wait(self.turn_delay_ms)

    def _wait_until_closed(self, current_turn: int) -> None:
        """Keep drawing the final state until the window closes."""
        running = True
        while running:
            running = self._handle_events()
            self._draw(current_turn)
            self.clock.tick(30)

    def _wait(self, delay_ms: int) -> bool:
        """Wait for a duration while processing window events."""
        elapsed = 0
        while elapsed < delay_ms:
            if not self._handle_events():
                return False
            elapsed += self.clock.tick(30)
        return True

    def _handle_events(self) -> bool:
        """Process window events and report whether to keep running."""
        for event in self.pygame.event.get():
            if event.type == self.pygame.QUIT:
                return False
        return True

    def _draw(self, current_turn: int) -> None:
        """Draw the full renderer scene for a turn."""
        self.screen.fill(BACKGROUND_COLOR)
        self._draw_connections()
        self._draw_zones()
        self._draw_drones()
        self._draw_turn_number(current_turn)
        self.pygame.display.flip()

    def _draw_connections(self) -> None:
        """Draw all map connections."""
        for connection in self.map_data.connections:
            start = self.zone_positions[connection.zone_a]
            end = self.zone_positions[connection.zone_b]
            self.pygame.draw.line(
                self.screen,
                CONNECTION_COLOR,
                start,
                end,
                3,
            )

    def _draw_zones(self) -> None:
        """Draw all zones and their labels."""
        for zone_name, position in self.zone_positions.items():
            zone = self.map_data.zones[zone_name]
            color = self._zone_color(zone_name)
            self.pygame.draw.circle(
                self.screen,
                color,
                position,
                ZONE_RADIUS,
            )
            self.pygame.draw.circle(
                self.screen,
                ZONE_BORDER_COLOR,
                position,
                ZONE_RADIUS,
                2,
            )

            type_label = self._zone_type_label(zone_name)
            if type_label:
                label = self.small_font.render(type_label, True, TEXT_COLOR)
                label_rect = label.get_rect(
                    center=(position[0], position[1] - 6)
                )
                self.screen.blit(label, label_rect)

            label = self.small_font.render(zone.name, True, TEXT_COLOR)
            label_rect = label.get_rect(
                center=(position[0], position[1] + ZONE_RADIUS + 14)
            )
            self.screen.blit(label, label_rect)

    def _zone_color(self, zone_name: str) -> tuple[int, int, int]:
        """Return the display color for a zone."""
        if zone_name == self.map_data.start_name:
            return START_COLOR
        if zone_name == self.map_data.end_name:
            return END_COLOR

        zone = self.map_data.zones[zone_name]
        match zone.zone_type:
            case ZoneType.PRIORITY:
                return PRIORITY_COLOR
            case ZoneType.RESTRICTED:
                return RESTRICTED_COLOR
            case ZoneType.BLOCKED:
                return BLOCKED_COLOR
            case _:
                return NORMAL_COLOR

    def _zone_type_label(self, zone_name: str) -> str:
        """Return the label shown inside a zone."""
        if zone_name == self.map_data.start_name:
            return "START"
        if zone_name == self.map_data.end_name:
            return "GOAL"

        zone = self.map_data.zones[zone_name]
        match zone.zone_type:
            case ZoneType.PRIORITY:
                return "PRIORITY"
            case ZoneType.RESTRICTED:
                return "RESTRICTED"
            case ZoneType.BLOCKED:
                return "BLOCKED"
            case _:
                return ""

    def _draw_drones(self) -> None:
        """Draw drone icons at their current zones."""
        visible_by_zone: dict[str, list[int]] = {}
        for drone_id, zone_name in self.positions.items():
            if zone_name not in self.zone_positions:
                continue
            visible_by_zone.setdefault(zone_name, []).append(drone_id)

        for zone_name, drone_ids in visible_by_zone.items():
            base_x, base_y = self.zone_positions[zone_name]
            for index, drone_id in enumerate(sorted(drone_ids)):
                offset_x = ((index % 4) - 1.5) * 18
                offset_y = (index // 4) * 18 - 26
                position = (int(base_x + offset_x), int(base_y + offset_y))
                image_rect = self.drone_image.get_rect(center=position)
                self.screen.blit(self.drone_image, image_rect)

                label = self.small_font.render(
                    str(drone_id),
                    True,
                    TEXT_COLOR,
                )
                label_rect = label.get_rect(
                    center=(position[0], position[1] + 19)
                )
                self.screen.blit(label, label_rect)

    def _draw_turn_number(self, current_turn: int) -> None:
        """Draw the current turn number."""
        text = self.font.render(
            f"Turn {current_turn}",
            True,
            TEXT_COLOR,
        )
        self.screen.blit(text, (20, 20))
