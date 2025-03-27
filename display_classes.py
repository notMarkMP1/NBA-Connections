import pygame
from classes import Vertex, PlayerData

class displayData:

    team_colours: dict[str, tuple[int, int, int]] = {
        "ATL": (225, 68, 52),   # Atlanta Hawks - Red
        "BOS": (0, 122, 51),    # Boston Celtics - Green
        "BKN": (0, 0, 0),       # Brooklyn Nets - Black
        "CHA": (29, 17, 96),    # Charlotte Hornets - Purple
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
        "PHX": (229, 95, 32),   # Phoenix Suns - Orange
        "POR": (224, 58, 62),   # Portland Trail Blazers - Red
        "SAC": (91, 43, 130),   # Sacramento Kings - Purple
        "SAS": (196, 206, 211), # San Antonio Spurs - Silver
        "TOR": (206, 17, 65),   # Toronto Raptors - Red
        "UTA": (0, 43, 92),     # Utah Jazz - Navy Blue
        "WAS": (0, 43, 92)      # Washington Wizards - Navy Blue
    }

    @staticmethod
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
    
    def update_position(self, mouse_delta: pygame.Vector2) -> None:
        """
        Shift the camera in the direction the mouse is dragging.
        """
        self.camera.topleft += (mouse_delta *0.1)
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

    position: pygame.Vector2
    node_size: float
    font_size: int
    object: pygame.rect
    color: tuple[int, int, int]
    font: pygame.font


    def __init__(self, position: pygame.Vector2, node_size: int, camera: Camera, screen: pygame.display):
        self.position = position
        self.node_size = node_size
        self.font_size = 12
        self.is_highlighted = False
        self.object = pygame.Rect(int(position.x), int(position.y), int(self.node_size), int(self.node_size))
        self.color = (255, 0, 0)
        self.text = pygame.font.Font(None, size=self.font_size).render("LEBRON JAMES!", True, (0, 0, 0))
        self.camera = camera
        self.screen = screen

    def scale_and_transform(self) -> None:
        """
        Scale and transform the object to place it where it should be according to the current camera position and zoom.
        """
        self.object.width = self.node_size * self.camera.zoom
        self.object.height = self.node_size * self.camera.zoom
        self.text = pygame.font.Font(None, size=int(self.font_size*self.camera.zoom)).render("LEBRON JAMES!", True, (0, 0, 0))
        self.object.x = self.position.x + self.camera.camera.left
        self.object.y = self.position.y + self.camera.camera.top

    def render(self) -> None:
        """
        Render the node in pygame according to the camera zoom and position.
        """
        if self.is_highlighted:
            pygame.draw.rect(self.screen, (0, 0, 0), self.object)
        else:
            pygame.draw.rect(self.screen, self.color, self.object)
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
        if collide:
            self.color = (255, 255, 255)
        else:
            self.color = (255, 0, 0)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                if collide:
                    print(f"Left mouse button clicked at {event.pos}")
                    self.is_highlighted = True
                else:
                    self.is_highlighted = False


class SearchBar:
    """
    A class that represents the interactive search bar.
    Allows text input to take the player to a specific player.
    """
    search_bar: pygame.rect
    text: str
    active: bool
    screen: pygame.display
    
    def __init__(self, position_x: int, position_y: int, width: int, height: int, screen: pygame.display) -> None:
        self.rect = pygame.Rect(position_x, position_y, width, height)
        self.text = ""
        self.active = False
        self.screen = screen

    def render(self, font: pygame.font.Font) -> None:
        """
        Render the search bar with its current state and text.
        """
        # Choose a color based on whether the search bar is active
        color = pygame.Color("azure3") if self.active else pygame.Color("black")
        pygame.draw.rect(self.screen, color, self.rect)
        #TODO: REFACTOR
        # Render the text inside the search bar (with a little padding)
        text = font.render(self.text, True, pygame.Color("white"))
        self.screen.blit(text, (self.rect.x + 5, self.rect.y + 5))

    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle events related to text input and focus.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Toggle active status if the search bar is clicked
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False

        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                print(f"Submitted search text: {self.text}")
                # Optionally clear text after submission:
                self.text = ""
            else:
                # Add the unicode of the key pressed to the search text
                self.text += event.unicode

        # Alternatively, you can use TEXTINPUT events instead of KEYDOWN for text input:
        # elif event.type == pygame.TEXTINPUT and self.active:
        #     self.text += event.text


class SideBar:
    """
    A class that represents the interactive sidebar present in the visualization feature.
    Allows searching for player names to view their profile in more depth and highlight them on screen.
    """

    sidebar: pygame.rect
    search_bar: SearchBar
    screen: pygame.display

    def __init__(self, SCREEN_WIDTH: int, SCREEN_HEIGHT: int, screen: pygame.display) -> None:
        SIDEBAR_WIDTH = 500
        SIDEBAR_HEIGHT = 900
        SIDEBAR_LEFT = SCREEN_WIDTH - SIDEBAR_WIDTH
        SIDEBAR_TOP = 0

        self.sidebar = pygame.Rect(SCREEN_WIDTH - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, SIDEBAR_HEIGHT)
        self.search_bar = SearchBar(SIDEBAR_LEFT + 10, SIDEBAR_TOP + 10, SIDEBAR_WIDTH - 20, SIDEBAR_HEIGHT / 20, screen)
        self.screen = screen

    def render(self) -> None:
        """
        Render the sidebar element on screen.
        """
        pygame.draw.rect(self.screen, pygame.Color("white"), self.sidebar)
        self.search_bar.render(pygame.font.Font(None, size=36))

    def check_interaction(self, events: list[pygame.event.Event]) -> None:
        """
        Handle interactions with the sidebar by passing each event to the subcomponents inside of the sidebar.
        """
        for event in events:
            self.search_bar.handle_event(event)