import pygame
import random
import math

import pygame.camera
from classes import Vertex, PlayerData, Graph

class DisplayData:
    """
    A data class containing ancillary information for the application.
    """
    teams: list[str] = [
        "ATL", "BOS", "BRK", "CHO", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
        "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
        "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"
    ]

    team_colours: dict[str, tuple[int, int, int]] = {
        "ATL": (225, 68, 52),   # Atlanta Hawks - Red
        "BOS": (0, 122, 51),    # Boston Celtics - Green
        "BRK": (0, 0, 0),       # Brooklyn Nets - Black
        "CHO": (29, 17, 96),    # Charlotte Hornets - Purple
        "CHI": (206, 17, 65),   # Chicago Bulls - Red
        "CLE": (134, 0, 56),    # Cleveland Cavaliers - Wine
        "DAL": (0, 83, 188),    # Dallas Mavericks - Blue
        "DEN": (13, 34, 64),    # Denver Nuggets - Midnight Blue
        "DET": (200, 16, 46),   # Detroit Pistons - Red
        "GSW": (29, 66, 138),   # Golden State Warriors - Royal Blue
        "HOU": (206, 17, 65),   # Houston Rockets - Red
        "IND": (0, 45, 98),     # Indiana Pacers - Navy Blue
        "LAC": (200, 16, 46),   # Los Angeles Clippers - Red
        "LAL": (85, 37, 130),   # Los Angeles Lakers - Purple
        "MEM": (93, 118, 169),  # Memphis Grizzlies - Navy Blue
        "MIA": (152, 0, 46),    # Miami Heat - Red
        "MIL": (0, 71, 27),     # Milwaukee Bucks - Green
        "MIN": (12, 35, 64),    # Minnesota Timberwolves - Navy Blue
        "NOP": (0, 22, 65),     # New Orleans Pelicans - Navy Blue
        "NYK": (0, 107, 182),   # New York Knicks - Blue
        "OKC": (0, 125, 195),   # Oklahoma City Thunder - Blue
        "ORL": (0, 125, 197),   # Orlando Magic - Blue
        "PHI": (0, 107, 182),   # Philadelphia 76ers - Blue
        "PHO": (229, 95, 32),   # Phoenix Suns - Orange
        "POR": (224, 58, 62),   # Portland Trail Blazers - Red
        "SAC": (91, 43, 130),   # Sacramento Kings - Purple
        "SAS": (196, 206, 211), # San Antonio Spurs - Silver
        "TOR": (206, 17, 65),   # Toronto Raptors - Red
        "UTA": (0, 43, 92),     # Utah Jazz - Navy Blue
        "WAS": (0, 43, 92)      # Washington Wizards - Navy Blue
    }

    def get_team_colour(self, team_name: str) -> tuple[int, int, int]:
        if team_name in self.team_colours:
            return self.team_colours[team_name]
        else:
            return (255, 255, 255)
        

class Camera:
    # TODO: MAKE MAXIMUM + MINIMUM ZOOM
    camera: pygame.rect
    zoom: float

    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.zoom = float(1.0)
        self.center = pygame.Vector2(width / 2, height / 2)
        self.width = width
        self.height = height

    def zoom_in(self) -> None:
        """
        Increase the camera zoom by 5%. If the zoom is greater than 3x, do not allow it to increase further.
        """
        self.zoom *= 1.05 
        if self.zoom > 3:
            self.zoom = 3
        return

    def zoom_out(self) -> None:
        """
        Decrease the camera zoom by 5%. If the zoom is less than 0.33x, do not allow it to decrease further.
        """
        self.zoom /= 1.05
        if self.zoom < 0.33:
            self.zoom = 0.33
        return
    
class PlayerNode:
    """
    a class that represents a player node on the graph. Can be interacted with to reveal more data about the player and
    highlight all of its connections. Maintains a reference to the camera and screen to adjust its rendering.
    """
    player_vertex: Vertex 
    player_data: PlayerData

    is_highlighted: bool

    camera: Camera
    screen: pygame.display

    node_size: float
    font_size: int
    object: pygame.rect
    default_color: tuple[int, int, int]
    color: tuple[int, int, int]

    def __init__(self,
                 position: pygame.Vector2,
                 node_size: int,
                 camera: Camera,
                 screen: pygame.display,
                 player_vertex: Vertex,
                 player_data: PlayerData):
        
        self.node_size = node_size
        self.font_size = 12
        self.is_highlighted = False
        self.object = pygame.Rect(int(position.x), int(position.y), int(self.node_size), int(self.node_size))
        
        self.camera = camera
        self.screen = screen
        self.player_vertex = player_vertex
        self.player_data = player_data
        self.default_color = DisplayData().team_colours[player_data.last_team]
        self.color = self.default_color

    def scale_and_transform(self) -> None:
        """
        Scale and transform the object to place it where it should be according to the current camera position and zoom.
        """
        self.object.width = self.node_size * self.camera.zoom
        self.object.height = self.node_size * self.camera.zoom

    def render(self) -> None:
        """
        Render the node in pygame according to the camera zoom and position.
        """
        if self.is_highlighted:
            pygame.draw.circle(self.screen, (0, 0, 0), self.object.center, self.object.width + 5)
            pygame.draw.circle(self.screen, self.color, self.object.center, self.object.width)
        else:
            pygame.draw.circle(self.screen, self.color, self.object.center, self.object.width)
        text = pygame.font.Font(None, size=int(self.font_size*self.camera.zoom)).render(f"{self.player_vertex.name}", True, (0, 0, 0))
        self.screen.blit(text, (self.object.center))

    def render_connections(self) -> None:
        """
        #TODO: DRAW THE FUCK ASS LINES FROM ONE NODE TO ANOTHER
        """
    
    def check_interaction(self, events: list[pygame.event.Event]) -> None:
        """
        Handle when the player interacts with this object. Highlight if the player mouses over, and load into the sidebar
        display if it gets clicked.
        """
        point = pygame.mouse.get_pos()
        collide = self.object.collidepoint(point)
    
        if collide:
            self.color = (200, 200, 200)
        else:
            self.color = self.default_color

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                if collide:
                    print(f"Left mouse button clicked at {event.pos}")
                    self.is_highlighted = True
                else:
                    self.is_highlighted = False

class TeamBox:
    """
    An object that references the teambox object at the top left of the screen, where a teams current players are displayed.
    """

    current_player_nodes: dict[str, PlayerNode]
    graph: Graph

    teambox: pygame.rect
    BOX_WIDTH = 1100
    BOX_HEIGHT = 450
    BOX_TOP = 0
    BOX_LEFT = 0

    screen: pygame.display
    camera: Camera
    sidebar: "SideBar"

    is_dragging: bool
    last_mouse_pos: tuple[int, int]

    def __init__(self, SCREEN_WIDTH: int,
                 SCREEN_HEIGHT: int,
                 screen: pygame.display, 
                 current_player_nodes: dict[str, PlayerNode],
                 graph: Graph) -> None:
        self.BOX_LEFT = 0
        self.BOX_TOP = 0

        self.teambox = pygame.Rect(self.BOX_LEFT, self.BOX_TOP, self.BOX_WIDTH, self.BOX_HEIGHT)
        self.camera = Camera(self.BOX_WIDTH, self.BOX_HEIGHT)
        self.screen = screen

        self.is_dragging = False
        last_mouse_pos = (0, 0)

        self.current_player_nodes = current_player_nodes
        self.graph = graph
    
    def add_references(self, sidebar: "SideBar") -> None:
        """Add references to the other major objects."""
        self.sidebar = sidebar
        
    def check_interaction(self, events: list[pygame.event.Event]) -> None:
        """
        Handle mouse inputs and such...
        """
        point = pygame.mouse.get_pos()
        collide = self.teambox.collidepoint(point)
        if (collide):
            for event in events:
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:  # Scroll up (zoom in)
                        self.camera.zoom_in()
                    elif event.y < 0:  # Scroll down (zoom out)
                        self.camera.zoom_out()

    def is_valid_point(self, new_point, existing_points, min_distance) -> bool:
        for point in existing_points:
            if math.dist(new_point, point) < min_distance:
                return False
        return True
    
    def get_points(self) -> list[tuple[int, int]]:

        # Define bounds

        radius = 30
        min_spacing = radius * 2  # Ensure circles don't overlap
        x_min, y_min = min_spacing, min_spacing
        x_max, y_max = self.BOX_WIDTH - min_spacing, self.BOX_HEIGHT - min_spacing

        points = []

        while len(points) < 24:
            new_point = (random.randint(x_min, x_max), random.randint(y_min, y_max))
            if self.is_valid_point(new_point, points, min_spacing):
                points.append(new_point)

        print(points)
        return points
    
    def generate_nodes(self, team: str) -> None:
        self.current_player_nodes.clear()
        circle_points = self.get_points()
        index = 0
        
        for player_name in self.graph.vertices:
            player_vertex = self.graph.vertices[player_name]
            if team == player_vertex.expanded_data.last_team:
                self.current_player_nodes[player_name] = PlayerNode(pygame.Vector2(circle_points[index][0], circle_points[index][1]),
                                                               30,
                                                               self.camera,
                                                               self.screen,
                                                               player_vertex,
                                                               player_vertex.expanded_data)
                index += 1

class OpponentBox:
    """
    An object that references the opponent box object at the bottom left of the screen, where a teams current opponents are displayed.
    """

class TeamButton:
    """
    An instance representing a button that changes the team displayed on the visualization tool. 
    """

    BUTTON_WIDTH = 100
    BUTTON_HEIGHT = 20
    BUTTON_LEFT: int = None
    BUTTON_TOP: int = None
    button: pygame.rect
    team: str
    teambox: TeamBox

    def __init__(self, screen: pygame.display, team: str, teambox: TeamBox, position_x: int, position_y: int) -> None:
        
        self.screen = screen
        self.team = team
        self.teambox = teambox
        self.BUTTON_LEFT = position_x
        self.BUTTON_TOP = position_y
        self.button = pygame.Rect(self.BUTTON_LEFT, self.BUTTON_TOP, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)

    def render(self) -> None:
        """Display this element."""
        pygame.draw.rect(self.screen, (200, 200, 200), self.button, border_radius=5)
        text = pygame.font.Font(None, size=22).render(f"{self.team}", True, (0, 0, 0))
        self.screen.blit(text, self.button.center)

    def check_interaction(self, events: list[pygame.event.Event]) -> None:
        """Handle interaction with this element."""
        point = pygame.mouse.get_pos()
        collide = self.button.collidepoint(point)
        if collide:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    self.teambox.generate_nodes(team=self.team)

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
            self.team_buttons.append(TeamButton(self.screen, team, self.teambox, start_x, start_y))
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
            team_button.check_interaction(events)

