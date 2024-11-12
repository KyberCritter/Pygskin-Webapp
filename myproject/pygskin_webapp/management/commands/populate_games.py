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

        # Fetch data from CFBDB
        cfbdb_params = {
            "year": 2024,
            "week": 12,
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

        # Fetch data from Odds API
        odds_params = {
            "regions": "us",
            "markets": "h2h,spreads,totals",
            "oddsFormat": "american",
            "dateFormat": "iso",
            "commenceTimeFrom": "2024-11-11T00:00:00Z",
            "commenceTimeTo": "2024-11-17T23:59:59Z",
            "apiKey": ODDS_API_KEY
        }
        odds_response = requests.get(ODDS_API_URL, params=odds_params)
        if odds_response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Failed to fetch Odds API data: {odds_response.status_code}"))
            return
        odds_data = odds_response.json()

        # Build a map for Odds API data by team names
        odds_team_map = defaultdict(list)
        for odds_game in odds_data:
            home_team = odds_game["home_team"]
            away_team = odds_game["away_team"]
            odds_team_map[home_team].append(odds_game)
            odds_team_map[away_team].append(odds_game)

        # Process each game from CFBDB
        for game_data in cfbdb_data:
            try:
                # Check if line data is available
                lines = game_data.get("lines", [])
                line_data = lines[0] if lines else None
                if not line_data:
                    self.stdout.write(self.style.WARNING(f"No line data for game ID {game_data['id']}"))
                    continue

                home_team_cfbdb = game_data["homeTeam"]
                away_team_cfbdb = game_data["awayTeam"]
                matched_game = None

                # Find the matching game in Odds API using substring matching
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

                # Initialize prices to None
                spread_price = None
                over_under_price = None
                if matched_game:
                    # Extract spread price
                    spread_market = next((mkt for bk in matched_game["bookmakers"] for mkt in bk["markets"] if mkt["key"] == "spreads"), None)
                    if spread_market:
                        spread_outcome = next((outcome for outcome in spread_market["outcomes"] if outcome["name"] == home_team_cfbdb or outcome["name"] == away_team_cfbdb), None)
                        if spread_outcome:
                            spread_price = spread_outcome.get("price")

                    # Extract over/under price
                    totals_market = next((mkt for bk in matched_game["bookmakers"] for mkt in bk["markets"] if mkt["key"] == "totals"), None)
                    if totals_market:
                        over_under_outcome = next((outcome for outcome in totals_market["outcomes"] if outcome["name"] in ["Over", "Under"]), None)
                        if over_under_outcome:
                            over_under_price = over_under_outcome.get("price")

                # Populate or update the Game table
                game, created = Game.objects.update_or_create(
                    cfbdb_game_id=game_data['id'],
                    defaults={
                        "season": game_data["season"],
                        "week": game_data["week"],
                        "home_team": home_team_cfbdb,
                        "away_team": away_team_cfbdb,
                        "home_money_line": line_data.get("homeMoneyline"),
                        "away_money_line": line_data.get("awayMoneyline"),
                        "spread": line_data.get("spread"),
                        "spread_price": spread_price,
                        "over_under": line_data.get("overUnder"),
                        "over_under_price": over_under_price,
                        "game_date": parse_datetime(game_data["startDate"])
                    }
                )

                # Populate or update GameScore table
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
