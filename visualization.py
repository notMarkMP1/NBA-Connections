# Example file showing a basic pygame "game loop"
import pygame
from classes import Vertex, PlayerData


class playerObject:
    player_vertex: Vertex 
    player_data: PlayerData
    position: pygame.Vector2
    radius: float

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
    clock = pygame.time.Clock()
    running = True
    dt = 0
    
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

    while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")

        pygame.draw.circle(screen, "red", player_pos, 40)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player_pos.y -= 300 * dt
        if keys[pygame.K_s]:
            player_pos.y += 300 * dt
        if keys[pygame.K_a]:
            player_pos.x -= 300 * dt
        if keys[pygame.K_d]:
            player_pos.x += 300 * dt

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000
    pygame.quit()


if __name__ == "__main__":
    start_visualization()