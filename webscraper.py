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
        time.sleep(4)

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


def players_played_with(player_id: str, max_retries: int = 3, retry_delay: int = 5) -> list:
    """
    Given a player_id, find all teammates of the player. Given the scope and length of requests,
    max_retries and retry_delay allow for multiple attempts in case of internet dropouts/connection hiccups.
    If omitted, max_retries defaults to 3 retries and a delay base of 5 (which grows by factor 1.5 per retry) seconds.

    Preconditions:
        - player_id is a valid player id found on basketball-reference.com
        - max_retries > 1
        - retry_delay > 0

    Returns a list of all names of players which player_id has played with.
    """

    url = f"https://www.basketball-reference.com/friv/teammates_and_opponents.fcgi?pid={player_id}&type=t"
    delay_exponent = 1.5
    request_timeout_seconds = 10
    players_list = []

    for attempt in range(max_retries):
        try:
            request = requests.get(url, timeout=request_timeout_seconds)
            request.raise_for_status()  # raise an exception for 4XX/5XX responses

            soup = BeautifulSoup(request.text, 'html.parser')
            # filter all td tags with attribute "data-stat" with value pid2 in it
            td_tags = soup.find_all("td", attrs={"data-stat": "pid2"})
            for tag in td_tags:
                players_list.append(tag.text.strip("*"))  # clean data
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


def generate_full_set() -> None:
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
        player_data = players_played_with(player)
        data[players[player]] = player_data
        cnt += 1
        print(f"Count: {cnt}/{len(players)} Player: {players[player]} Played with: {len(player_data)}")

        time.sleep(3.25)  # avoid ratelimit (1 request per 3s)

    with open("data/players_played_with.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'E9996'],
        'debug': False
    })

    # The below functions were run to generate the data
    # WARNING: running the webscraper will take approx ~6.25 hours with 5000+ web requests

    print("WARNING: running the full webscraper will take approx ~6.25 hours with 5000+ web requests.")
    run_scrape = input("Run the scraper? (Y/N) ")

    if run_scrape == "Y":
        scrape_all_players()  # generate "data/players.json"
        generate_full_set()  # generate the dataset
