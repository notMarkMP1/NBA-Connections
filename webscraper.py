"""
Webscraper for Project 2 of CSC111
Author: Mark Peng
"""


import time
import json
import csv

from bs4 import BeautifulSoup
import requests


URL_BASE = "https://www.basketball-reference.com/players/"


def scrape_all_players() -> None:
    """
    Scrapes for all player names and player ids and organizes into a dictionary where player id
    is the key and player name is the value.

    Does not return anything, stores a dictionary in json format at "data/players.json"
    """
    all_players = {}
    for letter in "abcdefghijklmnopqrstuvwxyz":
        url = URL_BASE + letter + "/"
        all_players.update(get_players_for_letter(url))
        print("Scraped player names for letter", letter)
        time.sleep(3.25)

    with open("data/players.json", "w", encoding="utf-8") as f:
        json.dump(all_players, f, indent=4)


def get_players_for_letter(url: str) -> dict:
    """
    Returns a dictionary mapping player id to player name of all NBA/ABA players
    with matching prefix for last name (e.g "a" for all players with last name starting with a)

    Preconditions:
        - url is a string of the form "https://www.basketball-reference.com/players/{letter}/"
          where letter is a character in "abcdefghijklmnopqrstuvwxyz"
    """
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser')
    players_dict = {}
    th_tags = soup.find_all("th", attrs={"data-append-csv": True})
    for tag in th_tags:
        full_name = tag.contents[0].text
        players_dict[tag.attrs["data-append-csv"]] = full_name.strip("*")
    return players_dict


def generate_players_json_from_csv(file: str) -> None:
    """
    From a csv file of all players, saves a json which maps player id and player name
    where player id is the key and player name is the value.
    Backup plan and showcase function due to rate limits on basketball-reference.com.

    Preconditions:
        - file is a valid csv file
        - file's csv header has player name first, player id last

    Returns nothing, instead saves a file at "data/players.json"
    """
    data = {}
    with open(file, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            if row:  # Check if row is not empty
                data[row[-1]] = row[0].strip("*")

    with open("data/players.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_players_json(file: str) -> dict:
    """
    Returns a dictionary of all players with player id as the key and
    player name as the value.

    Preconditions:
        - file is a valid json file
        - file is a json file which maps player id to player name
    """
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def scrape_individual_player(player_id: str, max_retries: int = 3, retry_delay: int = 5) -> dict:
    """
    Given a player_id, returns a dictionary of player data for the player.
    Given the scope and length of requests, max_retries and retry_delay allow for multiple attempts in case of internet dropouts/connection hiccups.
    If omitted, max_retries defaults to 3 retries and a delay base of 5 (which grows by factor 1.5 per retry) seconds.

    Returns a dictionary of player data.

    Preconditions:
        - player_id is a valid player id found on basketball-reference.com
        - max_retries > 1
        - retry_delay > 0

    """
    url = f"https://www.basketball-reference.com/players/{player_id[0]}/{player_id}.html"
    delay_exponent = 1.5
    request_timeout_seconds = 10
    player_data = {}
    
    for attempt in range(max_retries):
        try:
            request = requests.get(url, timeout=request_timeout_seconds)
            request.raise_for_status()  # raise an exception for 4XX/5XX responses
            
            soup = BeautifulSoup(request.text, 'html.parser')
            player_image = soup.find("img", attrs={"itemscope": "image"})
            totals_div = soup.find("div", attrs={"id": "div_totals_stats"})
            player_tables = totals_div.find("tbody")
            years_set = set()
            th_tags = player_tables.find_all("th", attrs={"data-stat": True})
            for tag in th_tags:
                years = tag.find_all("a")
                for year in years:
                    years_set.add(year.text)
            seasons = list(years_set)
            seasons.sort()

            player_footer = totals_div.find("tfoot")
            total_tr = player_footer.find("tr", attrs={"id": True})
            total_td = total_tr.find_all("td")
            players_stats = {}
            for tag in total_td:
                if tag.attrs["data-stat"] == "games":
                    players_stats["games"] = int(tag.text)
                elif tag.attrs["data-stat"] == "mp":
                    players_stats["minutes"] = int(tag.text)
                elif tag.attrs["data-stat"] == "fg":
                    players_stats["fg"] = int(tag.text)
                elif tag.attrs["data-stat"] == "fga":
                    players_stats["fga"] = int(tag.text)
                elif tag.attrs["data-stat"] == "fg_pct":
                    players_stats["fgp"] = float(tag.text)
                elif tag.attrs["data-stat"] == "fg3_pct":
                    players_stats["fg3p"] = float(tag.text)
                elif tag.attrs["data-stat"] == "fg2_pct":
                    players_stats["fg2p"] = float(tag.text)
                elif tag.attrs["data-stat"] == "ft_pct":
                    players_stats["ftp"] = float(tag.text)
                elif tag.attrs["data-stat"] == "pts":
                    players_stats["points"] = int(tag.text)
            
            last_team = player_tables.find_all("td", attrs={"data-stat": "team_name_abbr"})[-1].text
            first_team = player_tables.find_all("td", attrs={"data-stat": "team_name_abbr"})[0].text
            player_data["seasons"] = seasons
            player_data["active"] = True if "2024-25" in years_set else False
            player_data["last_team"] = last_team
            player_data["first_team"] = first_team
            player_data["stats"] = players_stats
            if player_image:
                player_data["image"] = player_image.attrs["src"]
            else:
                player_data["image"] = None 
            return player_data
            break
        except (requests.RequestException, requests.HTTPError) as e:
            if attempt < max_retries - 1:
                print(f"Error fetching data for {player_id}: {str(e)}. Retrying in {retry_delay} seconds... "
                      f"(Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                # increase backoff for subsequent retries
                retry_delay *= delay_exponent
            else:
                print(f"Failed to fetch data for {player_id} after {max_retries} attempts: {str(e)}")
                return []  # returns empty list in case of failure

def generate_all_player_stats() -> None:
    """
    Generates a json file with all player stats for all players in "data/players.json"
    """
    players = get_players_json("data/players.json")
    player_stats = {}
    cnt = 0
    for player in players:
        player_data = scrape_individual_player(player)
        player_stats[players[player]] = player_data
        cnt += 1
        print(f"Count: {cnt}/{len(players)} Player: {players[player]}")

        if cnt % 50 == 0 or cnt == len(players):
            print(f"Saving progress at {cnt} players...")
            with open("data/players_played_against_copy.json", "w", encoding="utf-8") as f:
                json.dump(player_stats, f, indent=4)
            print(f"Progress saved. Continuing...")

        time.sleep(3.25)  # avoid ratelimit (1 request per 3s)
    with open("data/players_stats.json", "w", encoding="utf-8") as f:
        json.dump(player_stats, f, indent=4)


def generate_all_missing_player_stats() -> None:
    """
    Fills in missing player stats due to failures.
    """
    players = get_players_json("data/players.json")
    player_stats = {}
    with open("data/players_stats.json", "r", encoding="utf-8") as f:
        player_stats = json.load(f)
    for player in player_stats:
        if type(player_stats[player]) == list:
            # find matching key for value in players
            for key, value in players.items():
                if value == player:
                    player_stats[player] = scrape_individual_player(key)
                    break
            print(f"Player: {player} Stats: {player_stats[player]}")
            time.sleep(3.25)  # avoid ratelimit (1 request per 3s)

    with open("data/players_stats.json", "w", encoding="utf-8") as f:
        json.dump(player_stats, f, indent=4)

def players_played_with(player_id: str, type: str, max_retries: int = 3, retry_delay: int = 5) -> list:
    """
    Given a player_id, find all teammates or opponents, depending on input, of the player. 
    Given the scope and length of requests, max_retries and retry_delay allow for multiple attempts in case of internet dropouts/connection hiccups.
    If omitted, max_retries defaults to 3 retries and a delay base of 5 (which grows by factor 1.5 per retry) seconds.

    Returns a list of all names of players which player_id has played with.

    Preconditions:
        - player_id is a valid player id found on basketball-reference.com
        - max_retries > 1
        - retry_delay > 0
        - type == "t" or type == "o"

    """

    url = f"https://www.basketball-reference.com/friv/teammates_and_opponents.fcgi?pid={player_id}&type={type}"
    delay_exponent = 1.5
    request_timeout_seconds = 10
    players_list =  []

    for attempt in range(max_retries):
        try:
            request = requests.get(url, timeout=request_timeout_seconds)
            request.raise_for_status()  # raise an exception for 4XX/5XX responses
            player_dict = {}
            soup = BeautifulSoup(request.text, 'html.parser')
            # filter all td tags with attribute "data-stat" with value pid2 in it
            tbody = soup.find("tbody")
            tr_tags = tbody.find_all("tr") if tbody else []
            for tag in tr_tags:
                td_tags = tag.find_all("td")
                teammate_data = [td.get_text().strip("*") for td in td_tags]
                if teammate_data and len(teammate_data) == 15:
                    player_dict = parse_player_data(teammate_data)
                    players_list.append(player_dict)
                elif 0 < len(teammate_data) < 15:
                    print(f"Error: {teammate_data} for {player_id}")
            break
        except (requests.RequestException, requests.HTTPError) as e:
            if attempt < max_retries - 1:
                print(f"Error fetching data for {player_id}: {str(e)}. Retrying in {retry_delay} seconds... "
                      f"(Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
                # increase backoff for subsequent retries
                retry_delay *= delay_exponent
            else:
                print(f"Failed to fetch data for {player_id} after {max_retries} attempts: {str(e)}")
                return []  # returns empty list in case of failure

    return players_list


def parse_player_data(player_data: list) -> dict:
    """
    Given a list of player data, returns a dictionary with keys as player names and values as
    a dictionary of player data.

    Preconditions:
        - player_data is a list of player data with length 15 and same format as per basketball-reference.com
    """
    player_dict = {}
    for idx in range(len(player_data)):
        if player_data[idx] == "":
            player_data[idx] = "0"
    player_dict["name"] = player_data[0]
    player_dict["games"] = player_data[1]
    player_dict["wins"] = player_data[2]
    player_dict["losses"] = player_data[3]
    player_dict["w_pct"] = player_data[4]
    player_dict["g_reg"] = player_data[6]
    player_dict["w_reg"] = player_data[7]
    player_dict["l_reg"] = player_data[8]
    player_dict["w_pct_reg"] = player_data[9]
    player_dict["g_ply"] = player_data[11]
    player_dict["w_ply"] = player_data[12]
    player_dict["l_ply"] = player_data[13]
    player_dict["w_pct_ply"] = player_data[14]
    return player_dict


def generate_players_played_with() -> None:
    """
    Given a dictionary of nba players with player id to player name key-value pairs,
    find all their teammates they have played with. Creates a dictionary mapping player name
    to a list of all player names which the player has been on a team with.

    Preconditions:
        - "data/players.json" is an existing file
        - "data/players.json" is a valid file mapping valid player id found on basketball-reference.com
           to player names

    Returns nothing.
    """

    data = {}
    players = get_players_json("data/players.json")
    cnt = 0

    for player in players:
        player_data = players_played_with(player, "t")
        data[players[player]] = player_data
        cnt += 1
        print(f"Count: {cnt}/{len(players)} Player: {players[player]} Played with: {len(player_data)}")
        time.sleep(3.25)  # avoid ratelimit (1 request per 3s)
    with open("data/players_played_with.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def generate_players_played_against() -> None:
    """
    Given a dictionary of nba players with player id to player name key-value pairs,
    find all their opponents they have played against. Creates a dictionary mapping player name
    to a list of all player names which the player has been on a team against.

    Preconditions:
        - "data/players.json" is an existing file
        - "data/players.json" is a valid file mapping valid player id found on basketball-reference.com
           to player names

    Returns nothing.
    """

    data = {}
    players = get_players_json("data/players.json")
    cnt = 0

    for i, player in enumerate(players):
        player_data = players_played_with(player, "o")
        data[players[player]] = player_data
        cnt += 1
        print(f"Count: {cnt}/{len(players)} Player: {players[player]} Played against: {len(player_data)}")
        
        # Save progress every 50 players
        if cnt % 50 == 0 or cnt == len(players):
            print(f"Saving progress at {cnt} players...")
            with open("data/players_played_against.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"Progress saved. Continuing...")
            
        time.sleep(3.25)  # avoid ratelimit (1 request per 3s)
    
    # Final save in case the total count wasn't divisible by 50
    if len(players) % 50 != 0:
        with open("data/players_played_against.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":

    # import python_ta

    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['R1705', 'E9998', 'E9999', 'E9996'],
    #     'debug': False
    # })

    # The below functions were run to generate the data
    # WARNING: running the webscraper will take approx ~6.25 hours with 5000+ web requests

    print("WARNING: running the all webscraper will take days with 15000+ web requests total.")
    player_scrape = input("Scrape all players? (Y/N) ")
    if player_scrape == "Y":
        print("Starting scrape")
        scrape_all_players()  # generate "data/players.json"
    teammate_scrape = input("Scrape all teammates of players? (Y/N) (requires players.json) ")
    if teammate_scrape == "Y":
        print("Starting scrape")
        generate_players_played_with()  # generate the dataset
    opponent_scrape = input("Scrape all opponents of players? (Y/N) (requires players.json) ")
    if opponent_scrape == "Y":
        print("Starting scrape")
        generate_players_played_against()  # generate the dataset
    player_stats_scrape = input("Scrape all player stats? (Y/N) (requires players.json) ")
    if player_stats_scrape == "Y":
        print("Starting scrape")
        generate_all_player_stats()
    else:
        generate_all_missing_player_stats()
        # print(len(players_played_with("jamesle01", "t")))
        # print(len(players_played_with("jamesle01", "o")))
        # scrape_individual_player("abdelal01")
        # scrape_individual_player("mahonbr01")
        # scrape_individual_player("jamesle01")
        ...
