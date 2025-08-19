"""
The main driver code. Run from this file to play the visualization tool.
"""
import asyncio
import json
import pygame
from visualization import Visualization

async def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    font = pygame.font.SysFont(None, 48)

    # Draw loading text
    screen.fill((30, 30, 30))
    text = font.render("Loading data...", True, (200, 200, 200))
    screen.blit(text, (160, 200))
    pygame.display.flip()

    # Let browser repaint
    await asyncio.sleep(0)

    # Load JSONs (synchronous)
    with open("players_stats.json", "r") as f:
        stats_data = json.load(f)

    await asyncio.sleep(0)  # Let browser repaint

    with open("active_players.json", "r") as f:
        player_connections = json.load(f)

    await asyncio.sleep(0)  # Let browser repaint

    # Start visualization
    pygameInstance = Visualization(stats_data, player_connections)
    await pygameInstance.start_visualization()

asyncio.run(main())