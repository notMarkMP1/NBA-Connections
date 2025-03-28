from typing import Optional
import pygame
import random
import math

import pygame.camera
from classes import Graph
from display_objects import PlayerNode, Camera, DisplayData, TeamButton


class DisplayBox: 
    """
    A class that provides methods for randomly generating points inside of a given bounds. 
    """

    box = pygame.rect
    BOX_WIDTH: int
    BOX_HEIGHT: int
    BOX_TOP: int
    BOX_LEFT: int

    screen: pygame.display
    camera: Camera

    def __init__(
                self, 
                screen: pygame.display, 
                width: int, 
                height: int, 
                left: int,
                top: int
                )  -> None:

        self.screen = screen
        self.camera = Camera()

        self.BOX_WIDTH = width
        self.BOX_HEIGHT = height
        self.BOX_LEFT = left
        self.BOX_TOP = top

        # Create a pygame.Rect representing the box bounds
        self.box = pygame.Rect(self.BOX_LEFT, self.BOX_TOP, self.BOX_WIDTH, self.BOX_HEIGHT)

    def check_interaction(self, events: list[pygame.event.Event]) -> None:
        """
        Handle mouse inputs and such...
        """
        point = pygame.mouse.get_pos()
        collide = self.box.collidepoint(point)
        if collide:
            for event in events:
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:  # Scroll up (zoom in)
                        self.camera.zoom_in()
                    elif event.y < 0:  # Scroll down (zoom out)
                        self.camera.zoom_out()

    def render(self) -> None:
        """Render itself, and all of the elements inside of it."""
        pygame.draw.rect(self.screen, (0, 0, 0), self.box, width=2, border_radius=2)

    def is_valid_point(self, new_point, existing_points, min_distance) -> bool:
        for point in existing_points:
            if math.dist(new_point, point) < min_distance:
                return False
        return True
    
    def get_points(self, num_of_players: int) -> tuple[list[tuple[int, int]], int]:
        """
        Given the bounds of the box and a certain number of circles to generate, randomly generate the placement of all of the circles and 
        the radius to set them to. If a random arrangement cannot be found within a reasonable amount of time,
        return an ordered arrangement of the circles instead.
        """
        if num_of_players < 1:
            return [], 0
        total_area = self.BOX_WIDTH * self.BOX_HEIGHT
        radius = min(int(math.sqrt((total_area // num_of_players) // math.pi)) // 4, 40)
        print(f"circle radius: {radius}")
        min_spacing = radius * 4

        x_min, y_min = self.BOX_LEFT + min_spacing, self.BOX_TOP + min_spacing
        x_max, y_max = self.BOX_LEFT + self.BOX_WIDTH - min_spacing, self.BOX_TOP + self.BOX_HEIGHT - min_spacing

        randomized_points = []
        default_points = []

        current_x, current_y = x_min, y_min

        for i in range(num_of_players):
            default_points.append((current_x, current_y))
            current_x += min_spacing
            if current_x >= x_max:
                current_x = x_min
                current_y += min_spacing

        count = 0
        MAX_ITERATIONS = 50000

        while len(randomized_points) < num_of_players and count < MAX_ITERATIONS:
            new_point = (random.randint(x_min, x_max), random.randint(y_min, y_max))
            if self.is_valid_point(new_point, randomized_points, min_spacing + 20):
                randomized_points.append(new_point)
            count += 1

        if len(randomized_points) == num_of_players:
            return randomized_points, radius
        else:
            return default_points, radius


class TeamBox(DisplayBox):
    """
    An object that references the teambox object at the top left of the screen, where a teams current players are displayed.
    Inherits from DisplayBox for all of the base methods.
    """

    current_player_nodes: dict[str, PlayerNode]
    graph: Graph

    sidebar: "SideBar"
    opponentbox : "OpponentBox"

    def __init__(self,
                 BOX_WIDTH: int,
                 BOX_HEIGHT: int,
                 BOX_LEFT: int,
                 BOX_TOP: int,
                 screen: pygame.display, 
                 graph: Graph) -> None:

        super().__init__(screen, BOX_WIDTH, BOX_HEIGHT,  BOX_LEFT, BOX_TOP)

        self.current_player_nodes = {}
        self.graph = graph
    
    def add_references(self, sidebar: "SideBar", opponentbox: "OpponentBox") -> None:
        """Add references to the other major objects."""
        self.sidebar = sidebar
        self.opponentbox = opponentbox
        
    def check_interaction(self, events: list[pygame.event.Event]) -> None:
        """
        Handle mouse inputs and such...
        """
        super().check_interaction(events)
        for node_name in self.current_player_nodes: # handle when a node gets clicked on, update opponent box
            result = self.current_player_nodes[node_name].check_interaction(events)
            if result:
                self.opponentbox.generate_nodes(result)

    def render(self) -> None:
        """Render itself, and all of the elements inside of it."""
        super().render()
        #pygame.draw.rect(self.screen, (0, 0, 0), self.teambox, width=2, border_radius=2)
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
            self.current_player_nodes[player[0]] = PlayerNode(pygame.Vector2(circle_points[index][0], circle_points[index][1]),
                                                                radius,
                                                                self.camera,
                                                                self.screen,
                                                                player[1],
                                                                player[1].expanded_data)
            index += 1

    
class OpponentBox(DisplayBox):
    """
    An object that references the opponent box object at the bottom left of the screen, where a players former teammmates are displayed.
    Inherits from the displaybox class for basic functionality.
    """

    current_player_nodes: dict[str, PlayerNode]
    graph: Graph

    sidebar: "SideBar"

    def __init__(self,
                 BOX_WIDTH: int,
                 BOX_HEIGHT: int,
                 BOX_LEFT: int,
                 BOX_TOP: int,
                 screen: pygame.display, 
                 graph: Graph) -> None:
        

        super().__init__(screen, BOX_WIDTH, BOX_HEIGHT,  BOX_LEFT, BOX_TOP)

        self.current_player_nodes = {}
        self.graph = graph

    def check_interaction(self, events: list[pygame.event.Event]) -> None:
        """
        Handle mouse inputs and such...
        """
        super().check_interaction(events)
        """for node_name in self.current_player_nodes: # handle when a node gets clicked on, update opponent box
            result = self.current_player_nodes[node_name].check_interaction(events)
            if result:
                print(result)"""

    def render(self) -> None:
        """Render itself, and all of the elements inside of it."""
        super().render()
        for node_name in self.current_player_nodes:
            player_node = self.current_player_nodes[node_name]
            player_node.scale_and_transform()
            player_node.render()


    def add_references(self, sidebar: "SideBar") -> None:
        """Add references to the other major objects."""
        self.sidebar = sidebar

    def generate_nodes(self, player: PlayerNode) -> None:
        """
        Given a player node, generate all of their connected nodes in the opponent box.
        """
        self.current_player_nodes.clear()

        opponents_to_generate = []
        for edge in player.player_vertex.neighbours:
            opponents_to_generate.append(edge.points_towards)

        circle_points, radius = super().get_points(len(opponents_to_generate))
        index = 0   

        for opponent in opponents_to_generate:
            self.current_player_nodes[opponent.name] = PlayerNode(pygame.Vector2(circle_points[index][0], circle_points[index][1]),
                                                                radius,
                                                                self.camera,
                                                                self.screen,
                                                                opponent,
                                                                opponent.expanded_data)
            index += 1
        
    

class StatList:
    """
    
    """

class SideBar:
    """
    A class that represents the interactive sidebar present in the visualization feature.
    Allows searching for player names to view their profile in more depth and highlight them on screen.
    """

    sidebar: pygame.rect
    screen: pygame.display
    teambox: TeamBox
    team_buttons: list[TeamButton]

    SIDEBAR_WIDTH = 500
    SIDEBAR_HEIGHT = 900
    SIDEBAR_TOP = None
    SIDEBAR_LEFT = None

    def __init__(self, SCREEN_WIDTH: int, SCREEN_HEIGHT: int, screen: pygame.display) -> None:

        self.SIDEBAR_LEFT = SCREEN_WIDTH - self.SIDEBAR_WIDTH
        self.SIDEBAR_TOP = 0

        self.sidebar = pygame.Rect(self.SIDEBAR_LEFT, self.SIDEBAR_TOP, self.SIDEBAR_WIDTH, self.SIDEBAR_HEIGHT)
        self.screen = screen
        self.team_buttons = []
    
    def add_references(self, teambox: TeamBox) -> None:
        """Maintain references to the other big objects."""
        self.teambox = teambox

    def build_sidebar(self) -> None:
        """Add all of the components of the sidebar in. Call after all references to other objects have been finalized."""
        start_x = self.SIDEBAR_LEFT + 60
        start_y = self.SIDEBAR_TOP + 10
        index = 1
        for team in DisplayData().teams:
            self.team_buttons.append(TeamButton(self.screen, team, start_x, start_y))
            start_x += 120
            if index % 3 == 0:
                start_y += 30
                start_x = self.SIDEBAR_LEFT + 60
            index += 1

    def render(self) -> None:
        """
        Render the sidebar element on screen.
        """
        pygame.draw.rect(self.screen, pygame.Color("white"), self.sidebar)
        for team_button in self.team_buttons:
            team_button.render()

    def check_interaction(self, events: list[pygame.event.Event]) -> None:
        """
        Handle interactions with the sidebar by passing each event to the subcomponents inside of the sidebar.
        """
        for team_button in self.team_buttons:
            result = team_button.check_interaction(events)
            if result:
                self.teambox.generate_nodes(result)


