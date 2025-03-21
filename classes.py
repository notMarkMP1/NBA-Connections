class PlayerData:
    name: str

class Vertex:
    name: str
    id: str
    expanded_data: PlayerData
    neighbours: set["Edge"] #  (DEFINITION: INTERSECTION BETWEEN TEAMMATES + FORMER TEAMMATES AND OPPONENTS)

    def check_connected() -> list["Vertex"]:
        """
        Return either None or a path of connections between the two players as a list of vertexes.
        """
    def check_teammate_score() -> float:
        """
        Return the "teammate" score between a player and another.
        """
    def check_winrate_correlation() -> float:
        """"
        Return the "teammate score" held between the current player and another player.
        """""
    
class Edge:
    points_towards: Vertex
    win_rate: float
    games_played: int


class Graph:
    vertices: dict[str, Vertex]
    def check_winrate_correlation() -> float:
        """
        Iterate through all of the vertexs and average their winrate_correlation() to get a stat.
        """


