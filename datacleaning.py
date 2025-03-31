"""
Code that was used to clean our datasets and create active_players.json
### LIST OF TASKS ###
# Number 1 - Get a list of all active players
#          - Extract all the names and choose where they get saved (do we want to filter players.json?) -> logical
# Number 2 - Filter out players played with json
#          - Test with a smaller size
# Number 3 - Filter out players played against json
# Number 4 - I need the intersection of players played against and with -> (teammates n opponents) n active
"""

import json

# Generate a list of active players
active_players = set()

with open('players_stats.json', 'r') as openfile:
    data = json.load(openfile)
    for name, info in data.items():
        if info['active']:
            active_players.add(name)

# print(len(active_players), active_players)
with open('players_played_with.json', 'r') as openfile:
    played_with = json.load(openfile)

with open('players_played_against.json', 'r') as openfile:  # This WILL be bombing my computer
    played_against = json.load(openfile)

dic = {}

for player in active_players:
    teammates, opponents = set(), set()

    for entry in played_with.get(player, []):
        teammates.add(entry['name'])

    for entry in played_against.get(player, []):
        opponents.add(entry['name'])

    shared_names = (teammates.union(opponents)).union(active_players)

    dic[player] = []

    for shared_player in shared_names:
        teammate_stats = next((x for x in played_with.get(player, []) if x['name'] == shared_player), None)
        opponent_stats = next((x for x in played_against.get(player, []) if x['name'] == shared_player), None)

        if teammate_stats and opponent_stats:  # Only take if union
            dic[player].append({
                "name": shared_player,
                "teammate_stats": teammate_stats,
                "opponent_stats": opponent_stats
            })
