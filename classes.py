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
    neighbours: set[Edge]  # (DEFINITION: INTERSECTION BETWEEN TEAMMATES + FORMER TEAMMATES AND OPPONENTS)

    # Use the players_stats.json file for this since it's already formatted how we want it
    def __init__(self, player_name: str) -> None:
        """ Initialize a new vertex for a player with the given name

        For now, player data will be set elsewhere (another function), maybe define later
        """
        self.name = player_name
        self.expanded_data = None
        self.neighbours = set()

    def check_connected(self, name1: str, visited: set[Vertex]) -> Optional[list[Vertex]]:
        """
        Return either None or a path of connections between the two players as a list of vertexes.

        Preconditions:
            - self not in visited
        """
        if self.name == name1:
            return [self]

        visited.add(self)
        for n in self.neighbours:
            if n.points_towards not in visited:
                path = n.points_towards.check_connected(name1, visited)
                if path:
                    return [self] + path

        return None

    def calculate_average_teammate_winrate(self) -> float:
        """
        Return a player's teammate average winrate across every player they've been both teammates and opponents with.
        Include playoff stats
        """
        total_winrate = 0.0
        count = 0
        for n in self.neighbours:
            if 'w_pct' in n.teammate_stats:
                total_winrate += n.teammate_stats['w_pct']
                count += 1
        if count > 0:
            return total_winrate / count
        else:
            return 0.0

    def calculate_average_opponent_winrate(self) -> float:
        """
        Return a player's opponent average winrate across every player they've been both teammates and opponents with.
        Include playoff stats
        """
        total_winrate = 0.0
        count = 0
        for n in self.neighbours:
            if 'w_pct' in n.opponent_stats:
                total_winrate += n.opponent_stats['w_pct']
                count += 1
        if count > 0:
            return total_winrate / count
        else:
            return 0.0

    def check_winrate_correlation(self) -> float:
        """
        Calculate the absolute difference between the average opponent and teammmate winrates
        """
        return abs(self.calculate_average_teammate_winrate() - self.calculate_average_opponent_winrate())

    def compute_winrate_difference(self, name1: str) -> tuple[float, float]:
        """
        Calculate the differnce between this player's (self) average winrates for teammates and opponents versus
        their winrates for the other player's (name1) winrates
        """
        if name1 not in player_graph.vertices:
            return (0.0, 0.0)

        other_player = player_graph.vertices[name1]
        return (
            abs(self.calculate_average_teammate_winrate() - other_player.calculate_average_teammate_winrate()),
            abs(self.calculate_average_opponent_winrate() - other_player.calculate_average_opponent_winrate())
        )


class Graph:
    """Fill out this docstring"""
    vertices: dict[str, Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph"""
        self.vertices = {}


    def initialize_graph(self) -> None:
        with open('players_stats.json', 'r') as openfile:
            stats_data = json.load(openfile)

        for name, info in stats_data.items():
            # Add only the active players
            if info.get('active', False):
                self.add_vertex(name)
                player_stats = PlayerData(seasons=info.get('seasons', []),
                                        first_team=info.get('first_team', ''),
                                        last_team=info.get('last_team', ''),
                                        stats=info.get('stats', {}),
                                        image_link=info.get('image', ''))

                self.vertices[name].expanded_data = player_stats

        with open('active_players.json', 'r') as openfile:
            player_connections = json.load(openfile)

        for name, connections in player_connections.items():
            # Access the vertex of the player so we can add its edges
            player_vertex = self.vertices.get(name)

            # Shouldn't happen but be safe
            if not player_vertex:
                continue

            for connection in connections:
                other_name = connection['name']

                # Apparently we need to skip players not in the graph
                if other_name not in self.vertices:
                    continue

                tmt_stats = connection.get('teammate_stats', {})
                opp_stats = connection.get('opponent_stats', {})

                edge = Edge(points_towards=self.vertices[other_name],
                            teammate_stats=tmt_stats,
                            opponent_stats=opp_stats)

                player_vertex.neighbours.add(edge)

    def add_vertex(self, player_name: str) -> None:
        """Add a vertex representing a player with the given name to this graph

        This vertex has no neighbours upon initialization.
        """
        if player_name not in self.vertices:
            self.vertices[player_name] = Vertex(player_name)

    def check_winrate_correlation(self) -> float:
        """
        Iterate through all of the vertices and average their winrate_correlation() to get a stat.
        """
        total_correlation = 0.0
        count = 0
        for vertex in self.vertices.values():
            total_correlation += vertex.check_winrate_correlation()
            count += 1
        if count > 0:
            return total_correlation / count
        else:
            return 0.0


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

    def calculate_player_performance(self):
        """Calculate how well this player does in revenge matchups compared to their normal value"""
        if 'w_pct' in self.opponent_stats and 'w_pct' in self.teammate_stats:
            return abs(float(self.opponent_stats['w_pct']) - float(self.teammate_stats['w_pct']))
        else:
            return 0.0


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
