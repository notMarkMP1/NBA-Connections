class displayData:

    team_colours: dict[str, tuple[int, int, int]] = {
        "ATL": (225, 68, 52),   # Atlanta Hawks - Red
        "BOS": (0, 122, 51),    # Boston Celtics - Green
        "BKN": (0, 0, 0),       # Brooklyn Nets - Black
        "CHA": (29, 17, 96),    # Charlotte Hornets - Purple
        "CHI": (206, 17, 65),   # Chicago Bulls - Red
        "CLE": (134, 0, 56),    # Cleveland Cavaliers - Wine
        "DAL": (0, 83, 188),    # Dallas Mavericks - Blue
        "DEN": (13, 34, 64),    # Denver Nuggets - Midnight Blue
        "DET": (200, 16, 46),   # Detroit Pistons - Red
        "GSW": (29, 66, 138),   # Golden State Warriors - Royal Blue
        "HOU": (206, 17, 65),   # Houston Rockets - Red
        "IND": (0, 45, 98),     # Indiana Pacers - Navy Blue
        "LAC": (200, 16, 46),   # Los Angeles Clippers - Red
        "LAL": (85, 37, 130),   # Los Angeles Lakers - Purple
        "MEM": (93, 118, 169),  # Memphis Grizzlies - Navy Blue
        "MIA": (152, 0, 46),    # Miami Heat - Red
        "MIL": (0, 71, 27),     # Milwaukee Bucks - Green
        "MIN": (12, 35, 64),    # Minnesota Timberwolves - Navy Blue
        "NOP": (0, 22, 65),     # New Orleans Pelicans - Navy Blue
        "NYK": (0, 107, 182),   # New York Knicks - Blue
        "OKC": (0, 125, 195),   # Oklahoma City Thunder - Blue
        "ORL": (0, 125, 197),   # Orlando Magic - Blue
        "PHI": (0, 107, 182),   # Philadelphia 76ers - Blue
        "PHX": (229, 95, 32),   # Phoenix Suns - Orange
        "POR": (224, 58, 62),   # Portland Trail Blazers - Red
        "SAC": (91, 43, 130),   # Sacramento Kings - Purple
        "SAS": (196, 206, 211), # San Antonio Spurs - Silver
        "TOR": (206, 17, 65),   # Toronto Raptors - Red
        "UTA": (0, 43, 92),     # Utah Jazz - Navy Blue
        "WAS": (0, 43, 92)      # Washington Wizards - Navy Blue
    }

    @staticmethod
    def get_team_colour(self, team_name: str) -> tuple[int, int, int]:
        if team_name in self.team_colours:
            return self.team_colours[team_name]
        else:
            return (255, 255, 255)
        
