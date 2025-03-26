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

    camera: pygame.rect
    zoom: float

    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.zoom = float(1.0)
        self.center = pygame.Vector2(width / 2, height / 2)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Applies the camera transformation to an entity
        return entity - self.camera.topleft

    def zoom_in(self):
        old_zoom = self.zoom
        self.zoom *= 1.05  # Zoom in by 10%
    """
        # Adjust the camera position so that zooming occurs around the center
        self.camera.center = (self.camera.centerx, self.camera.centery)
        self.camera.width = self.width * self.zoom
        self.camera.height = self.height * self.zoom

        # Adjust the camera position to keep the center of the camera the same
        self.camera.topleft = self.center - pygame.Vector2(self.camera.width / 2, self.camera.height / 2)
    """
    def zoom_out(self):
        old_zoom = self.zoom
        self.zoom /= 1.05  # Zoom out by 10%
    """
        # Adjust the camera position so that zooming occurs around the center
        self.camera.center = (self.camera.centerx, self.camera.centery)
        self.camera.width = self.width * self.zoom
        self.camera.height = self.height * self.zoom

        # Adjust the camera position to keep the center of the camera the same
        self.camera.topleft = self.center - pygame.Vector2(self.camera.width / 2, self.camera.height / 2)
    """
    def update(self, target):
        # Update the camera to center on a target position
        x = -target.x + self.width / 2
        y = -target.y + self.height / 2

        # Keep the camera within bounds of the level

        self.camera.topleft = (x, y)

class PlayerObject:
    """
    a class that represents a player node on the graph. Can be interacted with to reveal more data about the player and
    highlight all of its connections.
    """
    player_vertex: Vertex 
    player_data: PlayerData
    position: pygame.Vector2
    size: float
    object: pygame.rect
    color: tuple[int, int, int]

    def __init__(self, position: pygame.Vector2, size: int):
        self.position = position
        self.size = size
        self.object = pygame.Rect(int(position.x), int(position.y), int(self.size), int(self.size))
        self.color = (255, 0, 0)

    def scale_and_transform(self, camera : Camera) -> None:
        """
        Scale and transform the object to place it where it should be according to the current camera position and zoom.
        """
        self.object.width = self.size * camera.zoom
        self.object.height = self.size * camera.zoom
        self.object.move_ip(camera.camera.topleft)
        #print(self.object.center)

    def render(self, screen: pygame.display, camera: Camera) -> None:
        """
        Render the node in pygame according to the camera zoom and position.
        """
        
        pygame.draw.rect(screen, self.color, self.object)
    
    def check_collision(self) -> None:
        """
        Evaluate if the mouse is currently on the object. 
        """

    def check_boolean(self) -> bool:
        """
        Evaluate if the object has been clicked by the mouse.
        """