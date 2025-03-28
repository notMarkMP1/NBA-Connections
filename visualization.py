# Example file showing a basic pygame "game loop"
import pygame
from classes import Graph, Vertex, PlayerData
from display_classes import PlayerNode, Camera, SearchBar, SideBar, DisplayData, TeamBox


class Visualization:
    """
    The main class that runs the visualization tool. Maintains references to the original graph structure,
    each of the indivdual player nodes, and the UI features.
    """

    current_player_nodes: dict[str, PlayerNode]
    graph: Graph
    sidebar: SideBar
    teambox: TeamBox
    screen: pygame.display
    camera: Camera
    clock: pygame.time.Clock

    running: bool
    is_dragging: bool
    last_mouse_pos: tuple[int, int]

    def __init__(self) -> None:
        """
        Initialize an instance of the visualization tool.
        """

        pygame.init()
        self.screen = pygame.display.set_mode((1600, 900))
        self.camera = Camera(1600, 900)
        self.clock = pygame.time.Clock()

        self.running = True
        self.is_dragging = False
        self.last_mouse_pos = pygame.mouse.get_pos()

        SCREEN_WIDTH = self.screen.get_width()
        SCREEN_HEIGHT = self.screen.get_height()

        self.sidebar = SideBar(SCREEN_WIDTH, SCREEN_HEIGHT, self.screen)
        self.teambox = TeamBox(SCREEN_WIDTH, SCREEN_HEIGHT, self.screen, self.camera)

        self.current_player_nodes = {}
        self.graph = Graph()
        self.teambox.generate_nodes(self.current_player_nodes, "TOR", self.graph)

    def generate_data(self) -> None:
        """
        Iterate through the graph and create playernodes for each player data point. Store in the playernodes
        map that maps their id to their playernode object.
        """
        team_names = DisplayData().teams
        
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
        for node_name in self.current_player_nodes:
            self.current_player_nodes[node_name].check_interaction(events)
    
    def render_elements(self) -> None:
        """
        Render all of the elements on screen. Whether the elements are visible or not is dependent on their internal state.
        """
        for node_name in self.current_player_nodes:
            player_node = self.current_player_nodes[node_name]
            player_node.scale_and_transform()
            player_node.render()
        self.sidebar.render()

    def start_visualization(self) -> None:
        """
        Run the main python visualization tool.
        """


        while self.running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:  # Scroll up (zoom in)
                        self.camera.zoom_in()
                    elif event.y < 0:  # Scroll down (zoom out)
                        self.camera.zoom_out()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:  # Right mouse button
                        self.is_dragging = True
                        self.last_mouse_pos = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 3:  # Right mouse button
                        self.is_dragging = False
                elif event.type == pygame.MOUSEMOTION and self.is_dragging:
                    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
                    mouse_delta = mouse_pos - self.last_mouse_pos
                    self.camera.update_position(mouse_delta)


            self.screen.fill("azure")
            self.check_interactions(events)
            self.render_elements()

            pygame.display.flip()

            self.clock.tick(144)

        pygame.quit()






if __name__ == "__main__":
    pygameInstance = Visualization()
    pygameInstance.start_visualization()