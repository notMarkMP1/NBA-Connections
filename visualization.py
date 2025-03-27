# Example file showing a basic pygame "game loop"
import pygame
from classes import Graph, Vertex, PlayerData
from display_classes import PlayerNode, Camera, SearchBar, SideBar


class Visualization:
    """
    The main class that runs the visualization tool. Maintains references to the original graph structure,
    each of the indivdual player nodes, and the UI features.
    """

    player_nodes: dict[str, PlayerNode]
    graph: Graph
    sidebar: SideBar
    screen: pygame.display
    camera: Camera

    def __init__(self) -> None:
        """
        Initialize an instance of the visualization tool.
        """
        self.player_nodes = {}
        self.sidebar = None
        self.screen = None
        self.camera = None
        self.graph = Graph()
        self.generate_data()

    def generate_data(self) -> None:
        """
        Iterate through the graph and create playernodes for each player data point. Store in the playernodes
        map that maps their id to their playernode object.
        """
        for player_name in self.graph.vertices:
            print(player_name)
    
    def initializeElements(self) -> None:
        """
        Generate all of the pygame instances of the elements to be displayed visually.
        """

    def check_interactions(self, events: list[pygame.event.Event]) -> None:
        """
        Given a list of actions that have happened in the current frame, iterate through all of the player nodes
        and the UI elements to check if any updates need to occur.
        """
        self.sidebar.check_interaction(events)
        for node_name in self.player_nodes:
            self.player_nodes[node_name].check_interaction(events)
    
    def render_elements(self) -> None:
        """
        Render all of the elements on screen. Whether the elements are visible or not is dependent on their internal state.
        """
        for node_name in self.player_nodes:
            player_node = self.player_nodes[node_name]
            player_node.scale_and_transform()
            player_node.render()
        self.sidebar.render()

    def start_visualization(self) -> None:
        """
        Run the main python visualization tool.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((1600, 900))
        self.camera = Camera(1600, 900)
        clock = pygame.time.Clock()

        running = True
        is_dragging = False
        last_mouse_pos = pygame.mouse.get_pos()
        SCREEN_WIDTH = self.screen.get_width()
        SCREEN_HEIGHT = self.screen.get_height()

        self.player_nodes["1"] = PlayerNode(pygame.Vector2(640, 360), 50, self.camera, self.screen)
        self.player_nodes["2"] = PlayerNode(pygame.Vector2(300, 200), 50, self.camera, self.screen)
        self.sidebar = SideBar(SCREEN_WIDTH, SCREEN_HEIGHT, self.screen)


        while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:  # Scroll up (zoom in)
                        self.camera.zoom_in()
                    elif event.y < 0:  # Scroll down (zoom out)
                        self.camera.zoom_out()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:  # Right mouse button
                        is_dragging = True
                        last_mouse_pos = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:  # Right mouse button
                        is_dragging = False
                elif event.type == pygame.MOUSEMOTION and is_dragging:
                    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                    mouse_delta = mouse_pos - last_mouse_pos
                    self.camera.update_position(mouse_delta)


            self.screen.fill("azure")
            self.check_interactions(events)
            self.render_elements()

            pygame.display.flip()

            clock.tick(60)

        pygame.quit()






if __name__ == "__main__":
    pygameInstance = Visualization()
    pygameInstance.start_visualization()