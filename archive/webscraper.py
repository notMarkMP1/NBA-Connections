"""
Webscraper for Project 2 of CSC111
Author: Mark Peng
"""


import time
import json
import csv
from typing import Any

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


def parse_individual_player(tags: Any) -> dict:
    """
    Given a list of tags, returns a dictionary of player data.
    
    Preconditions:
        - tags is a list of tags with player data
    """
    stat_mapping = {
        "games": ("games", int),
        "mp": ("minutes", int),
        "fg": ("fg", int),
        "fga": ("fga", int),
        "fg_pct": ("fgp", float),
        "fg3_pct": ("fg3p", float),
        "fg2_pct": ("fg2p", float),
        "ft_pct": ("ftp", float),
        "pts": ("points", int)
    }

    players_stats = {}
    for tag in tags:
        stat_type = tag.attrs.get("data-stat")
        if stat_type in stat_mapping:
            key, converter = stat_mapping[stat_type]
            try:
                players_stats[key] = converter(tag.text)
            except (ValueError, TypeError):
                # Handle empty or invalid values
                players_stats[key] = 0 if converter == int else 0.0
    return players_stats


def scrape_individual_player(player_id: str, max_retries: int = 3, retry_delay: int = 5) -> dict:
    """
    Given a player_id, returns a dictionary of player data for the player.
    Given the scope and length of requests, max_retries and retry_delay allow 
    for multiple attempts in case of internet dropouts/connection hiccups.
    If omitted, max_retries defaults to 3 retries and a delay base of 5 
    (which grows by factor 1.5 per retry) seconds.

    Returns a dictionary of player data.

    Preconditions:
        - player_id is a valid player id found on basketball-reference.com
        - max_retries > 1
        - retry_delay > 0
    """
    url = f"https://www.basketball-reference.com/players/{player_id[0]}/{player_id}.html"
    player_data = {}

    for attempt in range(max_retries):
        try:
            soup = get_player_soup(url)

            # Extract data from soup
            totals_div = soup.find("div", attrs={"id": "div_totals_stats"})
            player_data = extract_player_data(soup, totals_div)
            break
        except Exception as e:
            if not handle_retry(attempt, max_retries, retry_delay, player_id, e):
                return []  # returns empty list in case of failure
            retry_delay *= 1.5  # increase backoff for subsequent retries

    return player_data


def get_player_soup(url: str) -> BeautifulSoup:
    """Helper function to get soup from URL"""
    request = requests.get(url, timeout=10)
    request.raise_for_status()
    return BeautifulSoup(request.text, 'html.parser')


def extract_player_data(soup: BeautifulSoup, totals_div: Any) -> dict:
    """Helper function to extract player data from soup"""
    result = {}

    # get image
    player_image = soup.find("img", attrs={"itemscope": "image"})
    result["image"] = player_image.attrs["src"] if player_image else None

    # get seasons data
    player_tables = totals_div.find("tbody")
    years_set = extract_years(player_tables)
    seasons = sorted(list(years_set))

    # get team data
    team_cells = player_tables.find_all("td", attrs={"data-stat": "team_name_abbr"})

    # get stats
    footer = totals_div.find("tfoot")
    stats = parse_individual_player(footer.find("tr", attrs={"id": True}).find_all("td"))

    # assemble result
    result.update({
        "seasons": seasons,
        "active": "2024-25" in years_set,
        "last_team": team_cells[-1].text,
        "first_team": team_cells[0].text,
        "stats": stats
    })

    return result


def extract_years(player_tables: Any) -> set:
    """Helper function to extract years from player tables"""
    years_set = set()
    th_tags = player_tables.find_all("th", attrs={"data-stat": True})
    for tag in th_tags:
        years_set.update(year.text for year in tag.find_all("a"))
    return years_set


def handle_retry(attempt: int, max_retries: int, retry_delay: int, player_id: str, error: Exception) -> bool:
    """Helper function to handle retry logic. Returns True if should retry."""
    if attempt < max_retries - 1:
        print(f"Error fetching data for {player_id}: {str(error)}. Retrying in {retry_delay} seconds... "
              f"(Attempt {attempt + 1}/{max_retries})")
        time.sleep(retry_delay)
        return True
    else:
        print(f"Failed to fetch data for {player_id} after {max_retries} attempts: {str(error)}")
        return False


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
            print("Progress saved. Continuing...")

        time.sleep(3.25)  # avoid ratelimit (1 request per 3s)
    with open("data/players_stats.json", "w", encoding="utf-8") as f:
        json.dump(player_stats, f, indent=4)


def gen_all_missing_player_stats() -> None:
    """
    Fills in missing player stats due to failures.
    """
    players = get_players_json("data/players.json")
    with open("data/players_stats.json", "r", encoding="utf-8") as f:
        player_stats = json.load(f)
    for player in player_stats:
        if not isinstance(player_stats[player], list):
            continue

        # find matching key for value in players
        for key, value in players.items():
            if value == player:
                player_stats[player] = scrape_individual_player(key)
                print(f"Player: {player} Stats: {player_stats[player]}")
                time.sleep(3.25)  # avoid ratelimit (1 request per 3s)
                break

    with open("data/players_stats.json", "w", encoding="utf-8") as f:
        json.dump(player_stats, f, indent=4)


def players_played_with(player_id: str, s_type: str, max_retries: int = 3, retry_delay: int = 5) -> list:
    """
    Given a player_id, find all teammates or opponents, depending on input, of the player. 
    Given the scope and length of requests, max_retries and retry_delay allow for multiple 
    attempts in case of internet dropouts/connection hiccups.
    If omitted, max_retries defaults to 3 retries and a delay base of 5 
    (which grows by factor 1.5 per retry) seconds.

    Returns a list of all names of players which player_id has played with.

    Preconditions:
        - player_id is a valid player id found on basketball-reference.com
        - max_retries > 1
        - retry_delay > 0
        - type == "t" or type == "o"

    """

    url = f"https://www.basketball-reference.com/friv/teammates_and_opponents.fcgi?pid={player_id}&type={s_type}"
    delay_exponent = 1.5
    players_list = []

    for attempt in range(max_retries):
        try:
            request = requests.get(url, timeout=10)
            request.raise_for_status()  # raise an exception for 4XX/5XX responses
            soup = BeautifulSoup(request.text, 'html.parser')
            # filter all td tags with attribute "data-stat" with value pid2 in it
            tbody = soup.find("tbody")
            tr_tags = tbody.find_all("tr") if tbody else []
            for tag in tr_tags:
                teammate_data = [td.get_text().strip("*") for td in tag.find_all("td")]
                players_list.append(parse_player_data(teammate_data))
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
    if len(player_data) != 15:
        return None
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


def gen_players_played_with() -> None:
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


def gen_players_played_against() -> None:
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

    for player in enumerate(players):
        player_data = players_played_with(player, "o")
        data[players[player]] = player_data
        cnt += 1
        print(f"Count: {cnt}/{len(players)} Player: {players[player]} Played against: {len(player_data)}")

        # Save progress every 50 players
        if cnt % 50 == 0 or cnt == len(players):
            print(f"Saving progress at {cnt} players...")
            with open("data/players_played_against.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print("Progress saved. Continuing...")

        time.sleep(3.25)  # avoid ratelimit (1 request per 3s)

    # Final save in case the total count wasn't divisible by 50
    if len(players) % 50 != 0:
        with open("data/players_played_against.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)


def test_run_and_save() -> None:
    """
    Runs a small test scrape for a few players and saves the results into separate JSON files.
    This demonstrates functionality of scraping individual player data, teammates, and opponents.
    """
    players_test = ["jamesle01", "mahonbr01", "abdelal01"]
    test_player_data = {}
    test_teammates = {}
    test_opponents = {}

    for player_t in players_test:

        player_stats = scrape_individual_player(player_t)
        test_player_data[player_t] = player_stats

        time.sleep(3.25)  # avoid ratelimit

        teammates = players_played_with(player_t, "t")
        test_teammates[player_t] = teammates

        time.sleep(3.25)

        opponents = players_played_with(player_t, "o")
        test_opponents[player_t] = opponents

        time.sleep(3.25)

    # save results
    with open("test_player_data.json", "w", encoding="utf-8") as f:
        json.dump(test_player_data, f, indent=4)
    with open("test_teammates.json", "w", encoding="utf-8") as f:
        json.dump(test_teammates, f, indent=4)
    with open("test_opponents.json", "w", encoding="utf-8") as f:
        json.dump(test_opponents, f, indent=4)

    print("Test run completed and data saved to JSON files.")


if __name__ == "__main__":

    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999', 'E9996', 'W0718'],
        'debug': False
    })

    print("Do you want to do a small test run of the webscraper? ")
    print("No data will be saved, and this will take around 50 seconds.")
    print("The extracted information will simply be printed to console.")
    test_run = input("Do you want to do a small test run? (Y/N) ")
    if test_run == "Y":
        # Test run for a few players
        print("Starting test run")
        test_run_and_save()

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
        gen_players_played_with()  # generate the dataset
    opponent_scrape = input("Scrape all opponents of players? (Y/N) (requires players.json) ")
    if opponent_scrape == "Y":
        print("Starting scrape")
        gen_players_played_against()  # generate the dataset
    player_stats_scrape = input("Scrape all player stats? (Y/N) (requires players.json) ")
    if player_stats_scrape == "Y":
        print("Starting scrape")
        generate_all_player_stats()

    print("Done.")
    print(scrape_individual_player("jamesle01"))
