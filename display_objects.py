from typing import Optional
import pygame
from classes import Vertex, PlayerData


class DisplayData:
    """
    A data class containing ancillary information for the application, and some helper functions to move things around.
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
    
    def float_to_percentage(self, value: str) -> str:
        """Converts a float string to a percentage string with 2 decimal places."""
        return f"{(float(value)*100):.1f}%"


class Camera:
    # TODO: MAKE MAXIMUM + MINIMUM ZOOM
    camera: pygame.rect
    zoom: float

    def __init__(self):
        self.zoom = float(1.0)

    def zoom_in(self) -> None:
        """
        Increase the camera zoom by 5%. If the zoom is greater than 3x, do not allow it to increase further.
        """
        self.zoom *= 1.05 
        if self.zoom > 2:
            self.zoom = 2
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
        self.font_size = 16
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
        
        if self.color[0] + self.color[1] + self.color[2] > 200:
            text_color = (0, 0, 0)
        else:
            text_color = (255, 255, 255)

        text_surface = pygame.font.Font(None, size=int(self.font_size*self.camera.zoom)).render(f"{self.player_vertex.name}", True, text_color)
        text_position = text_surface.get_rect(center=self.object.center)
        self.screen.blit(text_surface, text_position)

    def render_connection(self, node: "PlayerNode") -> None:
        """
        Draw a line between this node and another, assumign that this node is the ENDPOINT. 
        """
        current_position = self.object.center
        other_position = node.object.center

        pygame.draw.line(self.screen, (200, 200, 200), current_position, other_position, 1)

    def check_interaction(self, events: list[pygame.event.Event]) -> Optional["PlayerNode"]:
        """
        Handle when the player interacts with this object. Highlight if the player mouses over, and depending if it was clicked or not,
        return itself as an object to the entity it belongs to.
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
                    self.is_highlighted = True
                    return self
                else:
                    self.is_highlighted = False
                    return None
                
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

    def __init__(self, screen: pygame.display, team: str, position_x: int, position_y: int) -> None:
        
        self.screen = screen
        self.team = team
        self.BUTTON_LEFT = position_x
        self.BUTTON_TOP = position_y
        self.button = pygame.Rect(self.BUTTON_LEFT, self.BUTTON_TOP, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)

    def render(self) -> None:
        """Display this element."""
        pygame.draw.rect(self.screen, DisplayData().get_team_colour(self.team), self.button, border_radius=5)
        text_surface = pygame.font.Font(None, size=22).render(f"{self.team}", True, (255, 255, 255))
        text_position = text_surface.get_rect(center=self.button.center)
        self.screen.blit(text_surface, text_position)

    def check_interaction(self, events: list[pygame.event.Event]) -> str:
        """Handle interaction with this element."""
        point = pygame.mouse.get_pos()
        collide = self.button.collidepoint(point)
        if collide:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    return self.team
                
class WinrateMetrics:
    """
    A class that represents the winrate display of each player. Gives their winrate % against all opponents, against former teammates,
    and their differences.
    """

    LIST_WIDTH: int
    LIST_HEIGHT: int
    LIST_LEFT: int
    LIST_TOP: int
    box: pygame.rect

    screen: pygame.display

    current_player: PlayerNode | None
    metrics: dict[str, str]
    
    def __init__(self, screen: pygame.display, width: int, height: int, position_x: int, position_y: int) -> None:
        self.screen = screen
        self.LIST_WIDTH = width
        self.LIST_HEIGHT = height
        self.LIST_LEFT = position_x
        self.LIST_TOP = position_y
        self.box = pygame.Rect(self.LIST_LEFT, self.LIST_TOP, self.LIST_WIDTH, self.LIST_HEIGHT)
        self.metrics = {}
        self.current_player = None

    def render(self) -> None:
        pygame.draw.rect(self.screen, (0, 0, 0), self.box, width=2, border_radius=2)
        if self.metrics != {}:
            title_surface = pygame.font.Font(None, size=24).render(f"Overall Winrate Statistics For {self.metrics["Name"]}", True, (0, 0, 0))
            title_position = title_surface.get_rect(topleft=(self.LIST_LEFT + 10, self.LIST_TOP + 20))
            self.screen.blit(title_surface, title_position)
            current_x = self.LIST_LEFT + 10
            current_y = self.LIST_TOP + 40
            for metric in self.metrics:
                if metric == "Name":
                    continue
                text_surface = pygame.font.Font(None, size=20).render(f"{metric}: {DisplayData().float_to_percentage(self.metrics[metric])}", True, (0, 0, 0))
                text_position = text_surface.get_rect(topleft=(current_x, current_y))
                current_y += 15
                self.screen.blit(text_surface, text_position)
    
    def update_current_player(self, new_player: PlayerNode) -> None:
        self.current_player = new_player
        player_vertex = self.current_player.player_vertex
        self.metrics["Name"] = player_vertex.name
        self.metrics["Winrate % With Former Teammates"] = player_vertex.calculate_average_teammate_winrate()
        self.metrics["Winrate % Against Former Teammates"] = player_vertex.calculate_average_opponent_winrate()
        self.metrics["Absolute Winrate Difference"] = player_vertex.check_winrate_correlation()
    
    def refresh(self) -> None:
        self.metrics = {}
        self.current_player = None

class HeadToHeadMetrics:
    """
    A class that represents the head to head metrics of the two players being currently compared.
    """
    LIST_WIDTH: int
    LIST_HEIGHT: int
    LIST_LEFT: int
    LIST_TOP: int
    box: pygame.rect

    screen: pygame.display

    current_player: PlayerNode | None
    current_opponent: PlayerNode | None
    metrics: dict[str, str]

    def __init__(self, screen: pygame.display, width: int, height: int, position_x: int, position_y: int) -> None:
        self.screen = screen
        self.LIST_WIDTH = width
        self.LIST_HEIGHT = height
        self.LIST_LEFT = position_x
        self.LIST_TOP = position_y
        self.box = pygame.Rect(self.LIST_LEFT, self.LIST_TOP, self.LIST_WIDTH, self.LIST_HEIGHT)
        self.metrics = {}
        self.current_player = None
        self.current_opponent = None

    def render(self) -> None:
        """"""
        pygame.draw.rect(self.screen, (0, 0, 0), self.box, width=2, border_radius=2)
        if self.metrics != {}:
            title_surface = pygame.font.Font(None, size=24).render(self.metrics["Title"], True, (0, 0, 0))
            title_position = title_surface.get_rect(topleft=(self.LIST_LEFT + 10, self.LIST_TOP + 20))
            self.screen.blit(title_surface, title_position)
            current_x = self.LIST_LEFT + 10
            current_y = self.LIST_TOP + 40
            for metric in self.metrics:
                if metric == "Title":
                    continue
                if isinstance(self.metrics[metric], float):
                    text_surface = pygame.font.Font(None, size=20).render(f"{metric}: {DisplayData().float_to_percentage(self.metrics[metric])}", True, (0, 0, 0))
                else:
                    text_surface = pygame.font.Font(None, size=20).render(f"{metric}: {self.metrics[metric]}", True, (0, 0, 0))
                text_position = text_surface.get_rect(topleft=(current_x, current_y))
                current_y += 15
                self.screen.blit(text_surface, text_position)

    def refresh(self) -> None:
        self.metrics = {}
        self.current_player = None
        self.current_opponent = None

    def update_display(self) -> None:
        """
        Check if both current_player and current_opponent are stored, and then load their metrics accordingly.
        """
        if self.current_player is not None and self.current_opponent is not None:
            player_data = self.current_player.player_vertex
            opponent_data = self.current_opponent.player_vertex
            self.metrics["Title"] = f"{player_data.name}'s Stats Against {opponent_data.name}"

            head_to_head_data = player_data.return_edge_info(opponent_data.name)["opponent_stats"]
            self.metrics["Games Played"] = head_to_head_data["games"]
            self.metrics["Winrate %"] = head_to_head_data["w_pct"]

            deviation_data = player_data.compute_winrate_difference(opponent_data)
            self.metrics["Deviation From Expected"] = deviation_data[1]

    def update_current_player(self, new_player: PlayerNode) -> None:
        self.current_player = new_player
    
    def update_current_opponent(self, new_player: PlayerNode) -> None:
        self.current_opponent = new_player
        self.update_display()

class StatList:
    """
    A class that represents the stats display of each player. Gives their name, basic stats, and more. 
    """ 

    LIST_WIDTH: int
    LIST_HEIGHT: int
    LIST_LEFT: int
    LIST_TOP: int
    box: pygame.rect

    screen: pygame.display

    current_player: PlayerNode | None
    stats: dict[str, str]

    def __init__(self, screen: pygame.display, width: int, height: int, position_x: int, position_y: int) -> None:
        self.screen = screen
        self.LIST_WIDTH = width
        self.LIST_HEIGHT = height
        self.LIST_LEFT = position_x
        self.LIST_TOP = position_y
        self.box = pygame.Rect(self.LIST_LEFT, self.LIST_TOP, self.LIST_WIDTH, self.LIST_HEIGHT)
        self.stats = {}
        self.current_player = None

    def update_current_player(self, new_player: PlayerNode) -> None:
        self.current_player = new_player
        player_data = self.current_player.player_vertex.expanded_data
        self.stats = {}
        #TODO: TRY CATCH STATEMENTS FOR THIS BULLSHIT???
        self.stats["Name"] = self.current_player.player_vertex.name
        self.stats["First Season"] = player_data.seasons[0]
        self.stats["First Team"] = player_data.first_team
        self.stats["Current Team"] = player_data.last_team
        self.stats["Total Points"] = player_data.stats["points"]
        try:
            self.stats["Career Field Goal %"] = str(player_data.stats["fgp"])
            self.stats["Career 3PT Field Goal %"] = str(player_data.stats["fg3p"])
        except Exception as e:
            self.stats["Career Field Goal %"] = "N/A"
            self.stats["Career 3PT Field Goal %"] = "N/A"

    def render(self) -> None:
        pygame.draw.rect(self.screen, (0, 0, 0), self.box, width=2, border_radius=2)
        if self.stats != {}:
            title_surface = pygame.font.Font(None, size=24).render(f"{self.stats["Name"]}", True, (0, 0, 0))
            title_position = title_surface.get_rect(center=(self.LIST_LEFT + (self.LIST_WIDTH//2), self.LIST_TOP + 20))
            self.screen.blit(title_surface, title_position)
            #TODO: RENDER THE REST OF THE STATS
            current_x = self.LIST_LEFT + 10
            current_y = self.LIST_TOP + 50
            for stat in self.stats:
                if stat == "Name":
                    continue
                if isinstance(self.stats[stat], float):
                    text_surface = pygame.font.Font(None, size=20).render(f"{stat}: {DisplayData().float_to_percentage(self.stats[stat])}", True, (0, 0, 0))
                else:
                    text_surface = pygame.font.Font(None, size=20).render(f"{stat}: {self.stats[stat]}", True, (0, 0, 0))
                text_position = text_surface.get_rect(topleft=(current_x, current_y))
                current_y += 25
                self.screen.blit(text_surface, text_position)
    
    def refresh(self) -> None:
        self.stats = {}
        self.current_player = None