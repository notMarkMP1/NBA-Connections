"""
A module that contains the larger elements for the pygame visualization, e.g the sidebar and the graph
display boxes.
"""

import random
import math
import pygame


import pygame.camera
from classes import Graph
from display_objects import (
    PlayerNode,
    PositionalData,
    Camera,
    DisplayData,
    TeamButton,
    StatList,
    WinrateMetrics,
    HeadToHeadMetrics,
)


class DisplayBox:
    """
    A class that provides methods for randomly generating points inside of a given bounds.
    """

    box: pygame.rect
    positional_data: PositionalData
    screen: pygame.display
    camera: Camera

    def __init__(self, screen: pygame.display, positional_data: PositionalData) -> None:

        self.screen = screen
        self.camera = Camera()
        self.positional_data = positional_data

        # Create a pygame.Rect representing the box bounds
        self.box = pygame.Rect(self.positional_data.get_rect_positional_data())

    def check_interaction(self, events: list[pygame.event.Event]) -> None:
        """
        Handle mouse inputs and such...
        """
        point = pygame.mouse.get_pos()
        collide = self.box.collidepoint(point)
        if not collide:
            return None

        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Scroll up (zoom in)
                    self.camera.zoom_in()
                elif event.y < 0:  # Scroll down (zoom out)
                    self.camera.zoom_out()

    def render(self) -> None:
        """Render itself, and all of the elements inside of it."""
        pygame.draw.rect(self.screen, (0, 0, 0), self.box, width=2, border_radius=2)

    def is_valid_point(
        self,
        new_point: tuple[int, int],
        existing_points: list[tuple[int, int]],
        min_distance: int,
    ) -> bool:
        """
        Given a series of points already generated, return if the new point is outside of the minimum distance
        from all of the points.
        """
        for point in existing_points:
            if math.dist(new_point, point) < min_distance:
                return False
        return True

    def get_points(self, num_of_players: int) -> tuple[list[tuple[int, int]], int]:
        """
        Given the bounds of the box and a certain number of circles to generate,
        randomly generate the placement of all of the circles and
        the radius to set them to. If a random arrangement cannot be found within a
        reasonable amount of time,
        return an ordered arrangement of the circles instead.
        """
        if num_of_players < 1:
            return [], 0

        total_area = self.positional_data.width * self.positional_data.height
        radius = min(int(math.sqrt((total_area // num_of_players) // math.pi)) // 4, 40)
        min_spacing = radius * 4

        x_min, y_min = (
            self.positional_data.left + min_spacing,
            self.positional_data.top + min_spacing,
        )
        x_max, y_max = (
            self.positional_data.left + self.positional_data.width - min_spacing,
            self.positional_data.top + self.positional_data.height - min_spacing,
        )

        default_points = self.generate_default_points(
            num_of_players, (x_min, y_min, x_max), min_spacing
        )
        randomized_points = []
        count = 0

        while (
            len(randomized_points) < num_of_players and count < 50000
        ):  # reasonable runtime boudn on the while loop
            new_point = (random.randint(x_min, x_max), random.randint(y_min, y_max))
            if self.is_valid_point(new_point, randomized_points, min_spacing + 20):
                randomized_points.append(new_point)
            count += 1

        if len(randomized_points) == num_of_players:
            return randomized_points, radius
        else:
            return default_points, radius

    def generate_default_points(
        self, num_of_players: int, bounds: tuple[int, int, int], min_spacing: int
    ) -> list[tuple[int, int]]:
        """
        Given the bounds of a box, the number of points to generate inside of it, and the spacing between
        the points, create an ordered sequence of points.
        """
        default_points = []
        x_min, y_min, x_max = bounds
        current_x, current_y = x_min, y_min

        for i in range(num_of_players):
            default_points.append((current_x, current_y))
            current_x += min_spacing * 2
            if current_x >= x_max:
                current_x = x_min
                current_y += min_spacing
        return default_points


class TeamBox(DisplayBox):
    """
    An object that references the teambox object at the top left of the screen,
    where a teams current players are displayed.
    Inherits from DisplayBox for all of the base methods.
    """

    current_player_nodes: dict[str, PlayerNode]
    graph: Graph

    sidebar: "SideBar"
    opponentbox: "OpponentBox"

    def __init__(
        self,
        positional_data: PositionalData,
        screen: pygame.display,
        graph: Graph,
    ) -> None:

        super().__init__(screen, positional_data)

        self.current_player_nodes = {}
        self.graph = graph

    def add_references(self, sidebar: "SideBar", opponentbox: "OpponentBox") -> None:
        """Add references to the other major objects."""
        self.sidebar = sidebar
        self.opponentbox = opponentbox

    def check_interaction(self, events: list[pygame.event.Event]) -> None:
        """
        Handle interaction with thie box. When an element inside of the box is clicked, update
        the opponent box and the sidebar displays accordingly.
        """
        super().check_interaction(events)
        point = pygame.mouse.get_pos()
        collide = self.box.collidepoint(point)
        if collide:
            for node_name in self.current_player_nodes:
                result = self.current_player_nodes[node_name].check_interaction(events)
                if result:
                    self.opponentbox.generate_nodes(result)
                    self.sidebar.update_current_player(result)

    def render(self) -> None:
        """Render itself, and all of the elements inside of it."""
        super().render()
        # pygame.draw.rect(self.screen, (0, 0, 0), self.teambox, width=2, border_radius=2)
        for node_name in self.current_player_nodes:
            player_node = self.current_player_nodes[node_name]
            player_node.scale_and_transform()
            player_node.render()

    def generate_nodes(self, team: str) -> None:

        self.current_player_nodes.clear()
        players = []

        for player_name in self.graph.vertices:
            player_vertex = self.graph.vertices[player_name]
            if team == player_vertex.expanded_data.last_team:
                players.append((player_name, player_vertex))

        circle_points, radius = super().get_points(len(players))
        index = 0
        for player in players:
            self.current_player_nodes[player[0]] = PlayerNode(
                PositionalData(
                    radius,
                    radius,
                    circle_points[index][0],
                    circle_points[index][1],
                ),
                self.camera,
                self.screen,
                player[1],
            )
            index += 1


class OpponentBox(DisplayBox):
    """
    An object that references the opponent box object at the bottom left of the screen,
    where a players former teammmates are displayed.
    Inherits from the displaybox class for basic functionality.
    """

    current_player_nodes: dict[str, PlayerNode]
    graph: Graph

    reference_player: PlayerNode
    sidebar: "SideBar"

    def __init__(
        self,
        positional_data: PositionalData,
        screen: pygame.display,
        graph: Graph,
    ) -> None:

        super().__init__(screen, positional_data)

        self.current_player_nodes = {}
        self.graph = graph
        self.reference_player = None

    def check_interaction(self, events: list[pygame.event.Event]) -> None:
        """
        Handle mouse inputs and such...
        """
        super().check_interaction(events)
        point = pygame.mouse.get_pos()
        collide = self.box.collidepoint(point)
        if collide:
            for (
                node_name
            ) in (
                self.current_player_nodes
            ):  # handle when a node gets clicked on, update opponent box and sidebar
                result = self.current_player_nodes[node_name].check_interaction(events)
                if result:
                    self.sidebar.update_opponent_player(result)

    def render(self) -> None:
        """Render itself, and all of the elements inside of it."""
        super().render()
        for node_name in self.current_player_nodes:
            player_node = self.current_player_nodes[node_name]
            if self.reference_player is not None:
                player_node.render_connection(self.reference_player)

        for node_name in self.current_player_nodes:
            player_node = self.current_player_nodes[node_name]
            player_node.scale_and_transform()
            player_node.render()

    def add_references(self, sidebar: "SideBar") -> None:
        """Add references to the other major objects."""
        self.sidebar = sidebar

    def refresh(self) -> None:
        """
        Refresh the display to show nothing. Called when the user swaps to a new team.
        """
        self.current_player_nodes.clear()
        self.reference_player = None

    def generate_nodes(self, player: PlayerNode) -> None:
        """
        Given a player node, generate all of their connected nodes in the opponent box.
        """
        self.current_player_nodes.clear()
        self.reference_player = player

        opponents_to_generate = []
        for edge in player.player_vertex.neighbours:
            opponents_to_generate.append(edge.points_towards)

        circle_points, radius = super().get_points(len(opponents_to_generate))
        index = 0

        for opponent in opponents_to_generate:
            self.current_player_nodes[opponent.name] = PlayerNode(
                PositionalData(
                    radius,
                    radius,
                    circle_points[index][0],
                    circle_points[index][1],
                ),
                self.camera,
                self.screen,
                opponent,
            )
            index += 1


class SideBar:
    """
    A class that represents the interactive sidebar present in the visualization feature.
    Allows searching for player names to view their profile in more depth and highlight them on screen.
    """

    positional_data: PositionalData
    sidebar: pygame.rect
    screen: pygame.display

    teambox: TeamBox
    opponentbox: OpponentBox

    team_buttons: list[TeamButton]
    stat_displays: list[StatList, WinrateMetrics, HeadToHeadMetrics]

    def __init__(self, positional_data: PositionalData, screen: pygame.display) -> None:
        self.positional_data = positional_data
        self.sidebar = pygame.Rect(self.positional_data.get_rect_positional_data())
        self.screen = screen
        self.team_buttons = []
        self.stat_displays = []

    def add_references(self, teambox: TeamBox, opponentbox: OpponentBox) -> None:
        """Maintain references to the other big objects."""
        self.teambox = teambox
        self.opponentbox = opponentbox

    def build_sidebar(self) -> None:
        """
        Add all of the components of the sidebar in. Call after all references to
        other objects have been finalized.
        """
        start_x = self.positional_data.left + 75
        start_y = self.positional_data.top + 50
        index = 1
        for team in DisplayData().teams:
            self.team_buttons.append(TeamButton(self.screen, team, start_x, start_y))
            start_x += 120
            if index % 3 == 0:
                start_y += 30
                start_x = self.positional_data.left + 75
            index += 1
        # main stat display
        self.stat_displays.append(
            StatList(
                self.screen,
                PositionalData(
                    (self.positional_data.width - 20) // 2,
                    200,
                    self.positional_data.left + 10,
                    self.positional_data.height // 2,
                ),
            )
        )
        # opponent stat display
        self.stat_displays.append(
            StatList(
                self.screen,
                PositionalData(
                    (self.positional_data.width - 20) // 2,
                    200,
                    self.positional_data.left
                    + (self.positional_data.width - 20) // 2
                    + 15,
                    self.positional_data.height // 2,
                ),
            )
        )
        # overall winrate stat display
        self.stat_displays.append(
            WinrateMetrics(
                self.screen,
                PositionalData(
                    self.positional_data.width - 20,
                    100,
                    self.positional_data.left + 10,
                    self.positional_data.height // 2 + 220,
                ),
            )
        )
        # head to head winrate display
        self.stat_displays.append(
            HeadToHeadMetrics(
                self.screen,
                PositionalData(
                    self.positional_data.width - 20,
                    100,
                    self.positional_data.left + 10,
                    self.positional_data.height // 2 + 330,
                ),
            )
        )

    def render(self) -> None:
        """
        Render the sidebar element on screen.
        """
        pygame.draw.rect(self.screen, pygame.Color("white"), self.sidebar)
        team_text_surface = pygame.font.Font(None, size=32).render(
            "TEAMS", True, (0, 0, 0)
        )
        text_position = team_text_surface.get_rect(
            center=(
                (self.positional_data.left + self.positional_data.width // 2),
                self.positional_data.top + 25,
            )
        )
        self.screen.blit(team_text_surface, text_position)
        for team_button in self.team_buttons:
            team_button.render()
        for stat_display in self.stat_displays:
            stat_display.render()

    def check_interaction(self, events: list[pygame.event.Event]) -> None:
        """
        Handle interactions with the sidebar by passing each event to the subcomponents inside of the sidebar.
        """
        for team_button in self.team_buttons:
            result = team_button.check_interaction(events)
            if result:
                self.teambox.generate_nodes(result)
                self.opponentbox.refresh()
                for stat_display in self.stat_displays:
                    stat_display.refresh()

    def update_current_player(self, player: PlayerNode) -> None:
        """
        When a new player is clicked, update the sidebar displays accordingly with their data.
        """
        # only indexes 0, 2, 3 should be updated
        self.stat_displays[0].update_current_player(player)
        self.stat_displays[2].update_current_player(player)
        self.stat_displays[3].update_current_player(player)

    def update_opponent_player(self, player: PlayerNode) -> None:
        """
        When a new opponent is clicked, update the sidebar displays accordingly with their data.
        """
        # only indexes 1, 3 should be updated
        self.stat_displays[1].update_current_player(player)
        self.stat_displays[3].update_current_opponent(player)
