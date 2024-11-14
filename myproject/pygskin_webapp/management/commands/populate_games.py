import os 
import requests
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from pygskin_webapp.models import Game, GameScore
from collections import defaultdict

class Command(BaseCommand):
    help = 'Fetch and populate Games and GameScores from CFBDB and Odds API'

    def handle(self, *args, **options):
        # API URLs and API keys
        CFBDB_API_URL = "https://api.collegefootballdata.com/lines"
        ODDS_API_URL = "https://api.the-odds-api.com/v4/sports/americanfootball_ncaaf/odds"
        CFBDB_API_KEY = os.getenv("CFBDB_API_KEY")
        ODDS_API_KEY = os.getenv("ODDS_API_KEY")

        if not CFBDB_API_KEY or not ODDS_API_KEY:
            self.stdout.write(self.style.ERROR("API keys not set"))
            return

        # Get data from CFBDB
        # Right now, week/year is being set manually
        cfbdb_params = {
            "year": 2024,
            "week": 11,
            "provider": "ESPN Bet"
        }
        
        cfbdb_response = requests.get(
            CFBDB_API_URL,
            headers={"Authorization": f"Bearer {CFBDB_API_KEY}"},
            params=cfbdb_params
        )
        if cfbdb_response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Failed to fetch data: {cfbdb_response.status_code}"))
            return
        cfbdb_data = cfbdb_response.json()

        # Get data from Odds API
        # Right now, time for the week is being set manually
        odds_params = {
            "regions": "us",
            "bookmakers": "draftkings",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american",
            "dateFormat": "iso",
            "commenceTimeFrom": "2024-11-04T00:00:00Z",
            "commenceTimeTo": "2024-11-10T23:59:59Z",
            "apiKey": ODDS_API_KEY
        }
        odds_response = requests.get(ODDS_API_URL, params=odds_params)
        if odds_response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Failed to fetch Odds API data: {odds_response.status_code}"))
            return
        odds_data = odds_response.json()

        # Build a map for Odds API data by team names
        # This gets all the team names from Odds API and is used to map the games
        odds_team_map = defaultdict(list)
        for odds_game in odds_data:
            home_team = odds_game["home_team"]
            away_team = odds_game["away_team"]
            odds_team_map[home_team].append(odds_game)
            odds_team_map[away_team].append(odds_game)

        # Look at each game from CFBDB
        for game_data in cfbdb_data:
            try:
                # Check if game data is available
                lines = game_data.get("lines", [])
                line_data = lines[0] if lines else None
                if not line_data:
                    self.stdout.write(self.style.WARNING(f"No line data for game ID {game_data['id']}"))
                    continue

                home_team_cfbdb = game_data["homeTeam"]
                away_team_cfbdb = game_data["awayTeam"]
                matched_game = None

                # Find the matching game in Odds API using substring matching
                # Checking if CFBDB name is in Odds API name due to name mismatch
                for odds_team_name, odds_games in odds_team_map.items():
                    if home_team_cfbdb in odds_team_name:
                        for odds_game in odds_games:
                            if away_team_cfbdb in odds_game["away_team"] or away_team_cfbdb in odds_game["home_team"]:
                                matched_game = odds_game
                                break
                    elif away_team_cfbdb in odds_team_name:
                        for odds_game in odds_games:
                            if home_team_cfbdb in odds_game["home_team"] or home_team_cfbdb in odds_game["away_team"]:
                                matched_game = odds_game
                                break
                    if matched_game:
                        break

                # Initial spread prices and over/under prices
                # These are not always in the DB so must set to a default
                home_spread_price = None
                away_spread_price = None
                home_over_under_price = None
                away_over_under_price = None
                home_team_money_line = None
                away_team_money_line = None
                if matched_game:
                    # Get ML prices for home and away teams
                    money_line_market = next((mkt for bk in matched_game["bookmakers"] for mkt in bk["markets"] if mkt["key"] == "h2h"), None)
                    if money_line_market:
                        for outcome in money_line_market["outcomes"]:
                            if home_team_cfbdb in outcome["name"] or outcome["name"] in home_team_cfbdb:
                                home_team_money_line = outcome.get("price")
                            elif away_team_cfbdb in outcome["name"] or outcome["name"] in away_team_cfbdb:
                                away_team_money_line = outcome.get("price")

                    # Get spread prices for home and away teams with substring matching
                    spread_market = next((mkt for bk in matched_game["bookmakers"] for mkt in bk["markets"] if mkt["key"] == "spreads"), None)
                    if spread_market:
                        for outcome in spread_market["outcomes"]:
                            if home_team_cfbdb in outcome["name"] or outcome["name"] in home_team_cfbdb:
                                home_spread_price = outcome.get("price")
                            elif away_team_cfbdb in outcome["name"] or outcome["name"] in away_team_cfbdb:
                                away_spread_price = outcome.get("price")

                    # Get over/under prices for both teams
                    totals_market = next((mkt for bk in matched_game["bookmakers"] for mkt in bk["markets"] if mkt["key"] == "totals"), None)
                    if totals_market:
                        for outcome in totals_market["outcomes"]:
                            if outcome["name"] == "Over":
                                home_over_under_price = outcome.get("price")
                            elif outcome["name"] == "Under":
                                away_over_under_price = outcome.get("price")

                # Populate or update the Game table
                game, created = Game.objects.update_or_create(
                    cfbdb_game_id=game_data['id'],
                    defaults={
                        "season": game_data["season"],
                        "week": game_data["week"],
                        "home_team": home_team_cfbdb,
                        "away_team": away_team_cfbdb,
                        "home_money_line": home_team_money_line,
                        "away_money_line": away_team_money_line,
                        "spread": line_data.get("spread"),
                        "home_spread_price": home_spread_price,
                        "away_spread_price": away_spread_price,
                        "over_under": line_data.get("overUnder"),
                        "home_over_under_price": home_over_under_price,
                        "away_over_under_price": away_over_under_price,
                        "game_date": parse_datetime(game_data["startDate"])
                    }
                )

                # Populate or update GameScore table
                # When getting lines for a game that has not been played, score will be set to null
                # Will have to pull again at the end of the week to get the scores
                GameScore.objects.update_or_create(
                    game=game,
                    defaults={
                        "home_team_score": game_data.get("homeScore", 0),
                        "away_team_score": game_data.get("awayScore", 0)
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created new game: {game.home_team} vs {game.away_team}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Updated existing game: {game.home_team} vs {game.away_team}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing game ID {game_data['id']}: {e}"))
