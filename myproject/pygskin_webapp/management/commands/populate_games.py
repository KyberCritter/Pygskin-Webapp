import os 
import requests
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from pygskin_webapp.models import Game, GameScore

class Command(BaseCommand):
    help = 'Fetch and populate Games and GameScores from CFBDB'

    def handle(self, *args, **options):
        # API URL and API key
        CFBDB_API_URL = "https://api.collegefootballdata.com/lines"
        API_KEY = os.getenv("CFBDB_API_KEY")

        if not API_KEY:
            self.stdout.write(self.style.ERROR("CFBDB_API_KEY environment variable not set"))
            return

        params = {
            "year": 2024,
            "week": 11,
            "provider": "ESPN Bet", 
        }
        
        response = requests.get(
            CFBDB_API_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            params=params
        )

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Failed to fetch data: {response.status_code} - {response.text}"))
            return
        
        data = response.json()

        for game_data in data:
            try:
                # check if lines has data before accessing
                lines = game_data.get("lines", [])
                line_data = lines[0] if lines else None

                # Print error if there is no line data
                if not line_data:
                    self.stdout.write(self.style.ERROR("No line data"))

                # Populate game table
                game, created = Game.objects.update_or_create(
                    cfbdb_game_id=game_data['id'],
                    defaults={
                        "season": game_data["season"],
                        "week": game_data["week"],
                        "home_team": game_data["homeTeam"],
                        "away_team": game_data["awayTeam"],
                        "home_money_line": game_data["lines"][0].get("homeMoneyline"),
                        "away_money_line": game_data["lines"][0].get("awayMoneyline"),
                        "spread": game_data["lines"][0].get("spread"),
                        "over_under": game_data["lines"][0].get("overUnder"),
                    }
                )

                # Populate GameScore Table
                GameScore.objects.update_or_create(
                    game=game,
                    defaults={
                        "home_team_score": game_data["homeScore"],
                        "away_team_score": game_data["awayScore"],
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created new game: {game.home_team} vs {game.away_team}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Updated existing game: {game.home_team} vs {game.away_team}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing game ID {game_data['id']}: {e}"))