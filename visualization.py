# Example file showing a basic pygame "game loop"
import pygame
from classes import Vertex, PlayerData
from display_classes import displayData

class playerObject:
    player_vertex: Vertex 
    player_data: PlayerData
    position: pygame.Vector2
    radius: float


class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.zoom = 1.0
        self.center = pygame.Vector2(width / 2, height / 2)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Applies the camera transformation to an entity
        return entity - self.camera.topleft

    def apply_rect(self, rect):
        # Applies the camera transformation to a rectangle
        return rect.move(self.camera.topleft)

    def zoom_in(self):
        old_zoom = self.zoom
        self.zoom *= 1.1  # Zoom in by 10%

        # Adjust the camera position so that zooming occurs around the center
        self.camera.center = (self.camera.centerx, self.camera.centery)
        self.camera.width = self.width * self.zoom
        self.camera.height = self.height * self.zoom

        # Adjust the camera position to keep the center of the camera the same
        self.camera.topleft = self.center - pygame.Vector2(self.camera.width / 2, self.camera.height / 2)

    def zoom_out(self):
        old_zoom = self.zoom
        self.zoom /= 1.1  # Zoom out by 10%

        # Adjust the camera position so that zooming occurs around the center
        self.camera.center = (self.camera.centerx, self.camera.centery)
        self.camera.width = self.width * self.zoom
        self.camera.height = self.height * self.zoom

        # Adjust the camera position to keep the center of the camera the same
        self.camera.topleft = self.center - pygame.Vector2(self.camera.width / 2, self.camera.height / 2)

    def update(self, target):
        # Update the camera to center on a target position
        x = -target.x + self.width / 2
        y = -target.y + self.height / 2

        # Keep the camera within bounds of the level

        self.camera.topleft = (x, y)


def build_sidebar(SCREEN_WIDTH: int, SCREEN_HEIGHT: int) -> None:
    
    SIDEBAR_WIDTH = 100
    SIDEBAR_HEIGHT = 100
    
    sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)

    # Search bar setup
    search_rect = pygame.Rect(SIDEBAR_WIDTH + 20, 20, SCREEN_WIDTH - SIDEBAR_WIDTH - 40, 40)
    search_text = ''
    search_active = False

# pygame setup
def start_visualization() -> None:
    """
    Run the main python visualization tool.
    """
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    camera = Camera(1280, 720)
    clock = pygame.time.Clock()
    running = True
    dt = 0
    
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    last_mouse_pos = pygame.Vector2(0, 0)
    is_dragging = False

    while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    camera.zoom_in()
                elif event.button == 5:  # Scroll down
                    camera.zoom_out()
                elif event.button == 1:  # Left mouse button
                    is_dragging = True
                    last_mouse_pos = pygame.Vector2(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    is_dragging = False
            elif event.type == pygame.MOUSEMOTION and is_dragging:
                mouse_pos = pygame.Vector2(event.pos)
                # Calculate the difference in mouse position to move the camera
                mouse_delta = mouse_pos - last_mouse_pos
                camera.camera.topleft += mouse_delta
                last_mouse_pos = mouse_pos

            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Scroll up (zoom in)
                    camera.zoom_in()
                elif event.y < 0:  # Scroll down (zoom out)
                    camera.zoom_out()
    # Example drawing
        screen.fill("purple")

        pygame.draw.circle(screen, (255, 0, 0), camera.apply(pygame.Vector2(640, 360)), int(50 * camera.zoom))
        

        pygame.display.flip()

        camera.update(player_pos)
        player_rect = pygame.Rect(player_pos.x, player_pos.y, 40, 40)


    pygame.quit()


if __name__ == "__main__":
    start_visualization()




pygame.init()
screen = pygame.display.set_mode((800, 600))

clock = pygame.time.Clock()
running = True
