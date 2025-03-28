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
    is_visible: bool

    camera: Camera
    screen: pygame.display
    #TODO ADD A DEFAULT COLOR FIELD
    position: pygame.Vector2
    node_size: float
    font_size: int
    object: pygame.rect
    color: tuple[int, int, int]
    font: pygame.font

    def __init__(self,
                 position: pygame.Vector2,
                 node_size: int,
                 camera: Camera,
                 screen: pygame.display,
                 player_vertex: Vertex,
                 player_data: PlayerData):
        
        self.position = position
        self.node_size = node_size
        self.font_size = 12
        self.is_highlighted = False
        self.object = pygame.Rect(int(position.x), int(position.y), int(self.node_size), int(self.node_size))
        
        self.text = pygame.font.Font(None, size=12).render("LEBRON JAMES!", True, (0, 0, 0))
        self.camera = camera
        self.screen = screen
        self.player_vertex = player_vertex
        self.player_data = player_data
        self.color = DisplayData().team_colours[player_data.last_team]

    def scale_and_transform(self) -> None:
        """
        Scale and transform the object to place it where it should be according to the current camera position and zoom.
        """
        self.object.width = self.node_size * self.camera.zoom
        self.object.height = self.node_size * self.camera.zoom
        self.text = pygame.font.Font(None, size=int(self.font_size*self.camera.zoom)).render(f"{self.player_vertex.name}", True, (0, 0, 0))
        self.object.x = self.position.x + self.camera.camera.left
        self.object.y = self.position.y + self.camera.camera.top

    def render(self) -> None:
        """
        Render the node in pygame according to the camera zoom and position.
        """
        if self.is_highlighted:
            pygame.draw.circle(self.screen, self.color, self.object.center, self.object.width)
            #pygame.draw.rect(self.screen, (0, 0, 0), self.object)
        else:
            pygame.draw.circle(self.screen, self.color, self.object.center, self.object.width)
            #pygame.draw.rect(self.screen, self.color, self.object)
        self.screen.blit(self.text, (self.object.center))

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
        """
        if collide:
            self.color = (255, 255, 255)
        else:
            self.color = (255, 0, 0)
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                if collide:
                    print(f"Left mouse button clicked at {event.pos}")
                    self.is_highlighted = True
                else:
                    self.is_highlighted = False



class SideBar:
    """
    A class that represents the interactive sidebar present in the visualization feature.
    Allows searching for player names to view their profile in more depth and highlight them on screen.
    """

    sidebar: pygame.rect
    screen: pygame.display

    SIDEBAR_WIDTH = 500
    SIDEBAR_HEIGHT = 900
    SIDEBAR_TOP = None
    SIDEBAR_LEFT = None

    def __init__(self, SCREEN_WIDTH: int, SCREEN_HEIGHT: int, screen: pygame.display) -> None:

        self.SIDEBAR_LEFT = SCREEN_WIDTH - self.SIDEBAR_WIDTH
        self.SIDEBAR_TOP = 0

        self.sidebar = pygame.Rect(self.SIDEBAR_LEFT, self.SIDEBAR_TOP, self.SIDEBAR_WIDTH, self.SIDEBAR_HEIGHT)
        self.screen = screen

    def render(self) -> None:
        """
        Render the sidebar element on screen.
        """
        pygame.draw.rect(self.screen, pygame.Color("white"), self.sidebar)

    def check_interaction(self, events: list[pygame.event.Event]) -> None:
        """
        Handle interactions with the sidebar by passing each event to the subcomponents inside of the sidebar.
        """



class TeamBox:
    """
    An object that references the teambox object at the top left of the screen, where a teams current players are displayed.
    """

    teambox: pygame.rect
    BOX_WIDTH = 1100
    BOX_HEIGHT = 450
    BOX_TOP = 0
    BOX_LEFT = 0

    screen: pygame.display
    camera: Camera

    is_dragging: bool
    last_mouse_pos: tuple[int, int]

    def __init__(self, SCREEN_WIDTH: int, SCREEN_HEIGHT: int, screen: pygame.display) -> None:
        self.BOX_LEFT = 0
        self.BOX_TOP = 0

        self.teambox = pygame.Rect(self.BOX_LEFT, self.BOX_TOP, self.BOX_WIDTH, self.BOX_HEIGHT)
        self.screen = screen
        self.camera = Camera(self.BOX_WIDTH, self.BOX_HEIGHT)

        self.is_dragging = False
        last_mouse_pos = (0, 0)
        
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
    
    def generate_nodes(self,
                       current_player_nodes: dict[str, PlayerNode],
                       team: str,
                       graph: Graph
                       ) -> None:
        current_player_nodes.clear()
        circle_points = self.get_points()
        index = 0
        
        for player_name in graph.vertices:
            player_vertex = graph.vertices[player_name]
            if team == player_vertex.expanded_data.last_team:
                current_player_nodes[player_name] = PlayerNode(pygame.Vector2(circle_points[index][0], circle_points[index][1]),
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