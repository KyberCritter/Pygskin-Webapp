# File path: pygskin_webapp/management/commands/update_game_scores.py

import os
import requests
from django.core.management.base import BaseCommand
from pygskin_webapp.models import Game, GameScore
from django.utils.dateparse import parse_datetime

class Command(BaseCommand):
    help = 'Fetch and update game scores for completed games'

    def handle(self, *args, **options):
        # API for retrieving game scores
        CFBDB_API_URL = "https://api.collegefootballdata.com/lines"
        CFBDB_API_KEY = os.getenv("CFBDB_API_KEY")

        if not CFBDB_API_KEY:
            self.stdout.write(self.style.ERROR("CFBDB API key not set"))
            return

        season = 2024
        week = 11

        # Fetch scores data from the API
        params = {
            "year": season,
            "week": week
        }

        response = requests.get(
            CFBDB_API_URL,
            headers={"Authorization": f"Bearer {CFBDB_API_KEY}"},
            params=params
        )

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Failed to fetch scores data: {response.status_code}"))
            return

        scores_data = response.json()

        # Iterate over each game in the response
        for game_data in scores_data:
            cfbdb_game_id = game_data.get("id")
            home_score = game_data.get("homeScore")
            away_score = game_data.get("awayScore")

            # Skip if scores are not available
            if home_score is None or away_score is None:
                self.stdout.write(self.style.WARNING(f"Score not available yet for game ID {cfbdb_game_id}"))
                continue

            try:
                # Retrieve the corresponding Game and GameScore entries
                game = Game.objects.get(cfbdb_game_id=cfbdb_game_id)

                # Update or create GameScore entry
                GameScore.objects.update_or_create(
                    game=game,
                    defaults={
                        "home_team_score": home_score,
                        "away_team_score": away_score,
                        "last_updated": parse_datetime(game_data.get("start_date"))
                    }
                )

                self.stdout.write(self.style.SUCCESS(f"Updated scores for game {game.home_team} vs {game.away_team}: "f"{home_score} - {away_score}"))

            except Game.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"No game found with cfbdb_game_id: {cfbdb_game_id}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating score for game ID {cfbdb_game_id}: {e}"))
