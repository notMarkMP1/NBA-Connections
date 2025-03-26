# Example file showing a basic pygame "game loop"
import pygame
from classes import Vertex, PlayerData
from display_classes import PlayerObject, Camera




        





def build_sidebar(SCREEN_WIDTH: int, SCREEN_HEIGHT: int) -> None:
    
    SIDEBAR_WIDTH = 100
    SIDEBAR_HEIGHT = 100
    
    sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, SIDEBAR_HEIGHT)

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
    test_node = PlayerObject(pygame.Vector2(640, 360), 50)
    test_node_2 = PlayerObject(pygame.Vector2(300, 200), 50)
    running = True
    is_dragging = False
    last_mouse_pos = pygame.mouse.get_pos()
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

    while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Scroll up (zoom in)
                    camera.zoom_in()
                elif event.y < 0:  # Scroll down (zoom out)
                    camera.zoom_out()
                test_node.scale_and_transform(camera)
                test_node_2.scale_and_transform(camera)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    is_dragging = True
                    last_mouse_pos = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    is_dragging = False
            elif event.type == pygame.MOUSEMOTION and is_dragging:
                mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                # Calculate the difference in mouse position to move the camera
                mouse_delta = mouse_pos - last_mouse_pos
                camera.camera.topleft += (mouse_delta *0.01)
                test_node.scale_and_transform(camera)
                test_node_2.scale_and_transform(camera)
    # Example drawing
        screen.fill("purple")
        test_node.render(screen=screen, camera=camera)
        test_node_2.render(screen=screen, camera=camera)
        pygame.display.flip()
        camera.update(player_pos)


    pygame.quit()


if __name__ == "__main__":
    start_visualization()