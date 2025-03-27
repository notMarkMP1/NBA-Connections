# Using the data from our new generated file active_players.json, do the following
# 1. Create a graph with each vertex being a player
# 2. Each vertex will contain PlayerData, which is from player_stats.json
# 3. Each vertex will contain an edge to all the other players they are connected to (from active_players.json)

from __future__ import annotations
import json
from typing import Optional


class Vertex:
    """Fill out this docstring"""
    name: str
    expanded_data: Optional[PlayerData] = None
    neighbours: set[Edge]   # (DEFINITION: INTERSECTION BETWEEN TEAMMATES + FORMER TEAMMATES AND OPPONENTS)

    # Use the players_stats.json file for this since it's already formatted how we want it
    def __init__(self, player_name: str) -> None:
        """ Initialize a new vertex for a player with the given name

        For now, player data will be set elsewhere (another function), maybe define later
        """
        self.name = player_name
        self.expanded_data = None
        self.neighbours = set()

    # def check_connected(...) -> list[Vertex]:
        """
        Return either None or a path of connections between the two players as a list of vertexes.
        """
    # def check_teammate_score(...) -> float:
        """
        Return the "teammate" score between a player and another.
        """
    # def check_winrate_correlation(...) -> float:
        """"
        Return the "teammate score" held between the current player and another player.
        """""

      
class Graph:
    """Fill out this docstring"""
    vertices: dict[str, Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph"""
        self.vertices = {}

    def add_vertex(self, player_name: str) -> None:
        """Add a vertex representing a player with the given name to this graph

        This vertex has no neighbours upon initialization.
        """
        if player_name not in self.vertices:
            self.vertices[player_name] = Vertex(player_name)

    # def check_winrate_correlation(...) -> float:
        """
        Iterate through all of the vertexs and average their winrate_correlation() to get a stat.
        """

      
class Edge:
    """Fill out this docstring"""
    points_towards: Vertex
    teammate_stats: dict
    opponent_stats: dict

    def __init__(self, points_towards: Vertex, teammate_stats: dict, opponent_stats: dict) -> None:
        """Initialize an Edge connected to another player"""
        self.points_towards = points_towards
        self.teammate_stats = teammate_stats
        self.opponent_stats = opponent_stats

class PlayerData:
    """Fill out this docstring"""
    seasons: list[str]
    last_team: str
    first_team: str
    stats: dict[str, int]
    image_link: str

    def __init__(self, seasons: list[str], first_team: str, last_team: str, stats: dict[str, int], image_link: str):
        self.seasons = seasons
        self.first_team = first_team
        self.last_team = last_team
        self.stats = stats
        self.image_link = image_link


# Actual graph generation
# I don't know if we want to put all of this in a callable function later, but we can
player_graph = Graph()
with open('players_stats.json', 'r') as openfile:
    stats_data = json.load(openfile)

for name, info in stats_data.items():
    # Add only the active players
    if info.get('active', False):
        player_graph.add_vertex(name)

        player_stats = PlayerData(seasons=info.get('seasons', []),
                                  first_team=info.get('first_team', ''),
                                  last_team=info.get('last_team', ''),
                                  stats=info.get('stats', {}),
                                  image_link=info.get('image', ''))

        player_graph.vertices[name].expanded_data = player_stats

# print(player_graph.vertices["Stephen Curry"].expanded_data.stats)

with open('active_players.json', 'r') as openfile:
    player_connections = json.load(openfile)

for name, connections in player_connections.items():
    # Access the vertex of the player so we can add its edges
    player_vertex = player_graph.vertices.get(name)

    # Shouldn't happen but be safe
    if not player_vertex:
        continue

    for connection in connections:
        other_name = connection['name']

        # Apparently we need to skip players not in the graph
        if other_name not in player_graph.vertices:
            continue

        tmt_stats = connection.get('teammate_stats', {})
        opp_stats = connection.get('opponent_stats', {})

        edge = Edge(points_towards=player_graph.vertices[other_name],
                    teammate_stats=tmt_stats,
                    opponent_stats=opp_stats)

        player_vertex.neighbours.add(edge)

'''
Testing
vertex = player_graph.vertices.get("Immanuel Quickley")
if vertex:
    for edge in vertex.neighbours:
        print(f"{vertex.name} ↔ {edge.points_towards.name}")
        print(f"Teammate games: {edge.teammate_stats.get('games')}")
        print(f"Opponent games: {edge.opponent_stats.get('games')}")
        print("---")
'''
