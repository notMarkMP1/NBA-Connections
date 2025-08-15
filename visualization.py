"""
The file that contains the main visualization class.
"""
import pygame
from classes import Graph
from display_containers import SideBar, TeamBox, OpponentBox
from display_objects import PositionalData
import asyncio

class Visualization:
    """
    The main class that runs the visualization tool. Maintains references to the original graph structure,
    each of the indivdual player nodes, and the UI features.
    """
    graph: Graph
    sidebar: SideBar
    opponentbox: OpponentBox
    teambox: TeamBox
    screen: pygame.display
    clock: pygame.time.Clock
    running: bool

    def __init__(self, stats_data: dict, player_connections: dict) -> None:
        """
        Initialize an instance of the visualization tool.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((1600, 900))
        self.clock = pygame.time.Clock()
        self.running = True
        self.graph = Graph(stats_data, player_connections)
        self.teambox = TeamBox(PositionalData(1100, 450, 0, 0), self.screen, self.graph)
        self.sidebar = SideBar(PositionalData(500, 900, 1100, 0), self.screen)
        self.opponentbox = OpponentBox(PositionalData(1100, 450, 0, 450), self.screen, self.graph)
        self.teambox.add_references(self.sidebar, self.opponentbox)
        self.sidebar.add_references(self.teambox, self.opponentbox)
        self.opponentbox.add_references(self.sidebar)
        self.sidebar.build_sidebar()

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
        Render all of the elements on screen. Whether the elements are visible
        or not is dependent on their internal state.
        """
        self.opponentbox.render()
        self.teambox.render()
        self.sidebar.render()

    async def start_visualization(self) -> None:
        """
        Run the main python visualization tool.
        """
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            self.screen.fill((128, 128, 128))
            self.check_interactions(events)
            self.render_elements()
            pygame.display.flip()
            self.clock.tick(144)
            await asyncio.sleep(0)
        pygame.quit()

