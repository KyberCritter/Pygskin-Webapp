# File path: pygskin_webapp/management/commands/update_game_scores.py

import os
import requests
from django.core.management.base import BaseCommand
from pygskin_webapp.models import Game, GameScore, Bet, BettingTransaction, UserCredit
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
            start_date = game_data.get("start_date")

            # Skip if scores are not available
            if home_score is None or away_score is None:
                self.stdout.write(self.style.WARNING(f"Score not available yet for game ID {cfbdb_game_id}"))
                continue

            try:
                # Retrieve the corresponding Game and GameScore entries
                game = Game.objects.get(cfbdb_game_id=cfbdb_game_id)

                # Only parse start_date if it's a valid string
                last_updated = parse_datetime(start_date) if isinstance(start_date, str) else None

                # Update or create GameScore entry
                GameScore.objects.update_or_create(
                    game=game,
                    defaults={
                        "home_team_score": home_score,
                        "away_team_score": away_score,
                        "last_updated": last_updated
                    }
                )

                self.stdout.write(self.style.SUCCESS(f"Updated scores for game {game.home_team} vs {game.away_team}: "
                                                     f"{home_score} - {away_score}"))

                # Call method to update bet results
                self.update_bet_results(game, home_score, away_score)

            except Game.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"No game found with cfbdb_game_id: {cfbdb_game_id}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating score for game ID {cfbdb_game_id}: {e}"))

    def update_bet_results(self, game, home_score, away_score):
        # Get all of the pending bets
        pending_bets = Bet.objects.filter(game=game, status="Pending")

        for bet in pending_bets:
            won = False  # Tracks if bet was won
            payout = 0

            # Check outcome for money line
            if bet.bet_type == "Money Line":
                if (bet.odds > 0 and home_score > away_score) or (bet.odds < 0 and away_score > home_score):
                    won = True

            elif bet.bet_type == "Spread":
                spread_difference = (home_score - away_score) if bet.odds < 0 else (away_score - home_score)
                if spread_difference >= abs(float(bet.game.spread)):
                    won = True

            elif bet.bet_type == "Over Under":
                total_score = home_score + away_score
                if (bet.odds > 0 and total_score > float(bet.game.over_under)) or \
                        (bet.odds < 0 and total_score < float(bet.game.over_under)):
                    won = True

            if won:
                payout = int(bet.credits_bet * abs(float(bet.odds)) / 100)
                bet.status = "Won"
                self.update_user_credits(bet, payout, "Win")
            else:
                bet.status = "Lost"
                self.update_user_credits(bet, -bet.credits_bet, "Lose")

            # Update bet payout and save
            bet.payout = payout
            bet.save()

    def update_user_credits(self, bet, amount, transaction_type):
        # Update user credits and log the transaction
        user_credit = UserCredit.objects.get(user=bet.user)
        user_credit.total_credits += amount

        if amount > 0:
            user_credit.credits_won += amount
        else:
            user_credit.credits_lost += abs(amount)
        user_credit.save()

        # Record the transaction
        BettingTransaction.objects.create(
            user=bet.user,
            bet=bet,
            transaction_type=transaction_type,
            credits_adjusted=amount,
            balance_after_transaction=user_credit.total_credits
        )
