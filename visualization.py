# Example file showing a basic pygame "game loop"
import pygame
from classes import Graph, Vertex, PlayerData
from display_containers import PlayerNode, Camera, SideBar, DisplayData, TeamBox, OpponentBox


class Visualization:
    """
    The main class that runs the visualization tool. Maintains references to the original graph structure,
    each of the indivdual player nodes, and the UI features.
    """

    graph: Graph
    sidebar: SideBar
    teambox: TeamBox
    screen: pygame.display
    clock: pygame.time.Clock

    running: bool

    def __init__(self) -> None:
        """
        Initialize an instance of the visualization tool.
        """

        pygame.init()
        self.screen = pygame.display.set_mode((1600, 900))
        self.clock = pygame.time.Clock()

        self.running = True
        self.is_dragging = False
        self.last_mouse_pos = pygame.mouse.get_pos()

        SCREEN_WIDTH = self.screen.get_width()
        SCREEN_HEIGHT = self.screen.get_height()
        self.graph = Graph()
        
        self.teambox = TeamBox(1100, 450, 0, 0, self.screen, self.graph)
        self.sidebar = SideBar(SCREEN_WIDTH, SCREEN_HEIGHT, self.screen)
        self.opponentbox = OpponentBox(1100, 450, 0, 450, self.screen, self.graph)
        self.teambox.add_references(self.sidebar, self.opponentbox)
        self.sidebar.add_references(self.teambox)
        self.sidebar.build_sidebar()


        self.teambox.generate_nodes("TOR")

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
        self.teambox.check_interaction(events)
        self.opponentbox.check_interaction(events)
    
    def render_elements(self) -> None:
        """
        Render all of the elements on screen. Whether the elements are visible or not is dependent on their internal state.
        """
        self.teambox.render()
        self.sidebar.render()
        self.opponentbox.render()

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


            self.screen.fill("azure")
            self.check_interactions(events)
            self.render_elements()

            pygame.display.flip()

            self.clock.tick(144)

        pygame.quit()

if __name__ == "__main__":
    pygameInstance = Visualization()
    pygameInstance.start_visualization()