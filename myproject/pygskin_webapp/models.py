import hashlib
import os
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from pygskin import ModelType
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User

from django.conf import settings as conf_settings


class Coach(models.Model):
    """Model representing a coach."""
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    latest_team = models.CharField(max_length=100, default="")
    first_year_recorded = models.IntegerField(default=2001, validators=[MinValueValidator(2001), MaxValueValidator(2023)])
    last_year_recorded = models.IntegerField(default=2001, validators=[MinValueValidator(2001), MaxValueValidator(2023)])
    # Filename of a cybercoach model of the coach, could use any of the model types (all models are stored in the same directory)
    default_cybercoach_filename = models.CharField(max_length=100, default="")
    biography = models.TextField(max_length=1000, default="")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "Coach"
        verbose_name_plural = "Coaches"

class Cybercoach(models.Model):
    """Model representing a cybercoach. A cybercoach is a machine learning model that predicts the outcome of a game."""
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    # Model type (choices are from from pygskin.ModelType IntEnum)
    model_type = models.CharField(choices=[(model_type.name, model_type.value) for model_type in ModelType], max_length=100)
    # Filename of the cybercoach model (all models are stored in the same directory)
    model_filename = models.CharField(max_length=100, default="")
    file_hash = models.CharField(max_length=32, blank=True, editable=False) # Field to store the MD5 hash

    def __str__(self):
        return f"{self.coach.first_name} {self.coach.last_name} ({self.model_type})"
    
    class Meta:
        ordering = ["coach", "model_type"]
        verbose_name = "Cybercoach"
        verbose_name_plural = "Cybercoaches"

@receiver(post_save, sender=Cybercoach)
def calculate_file_hash(sender, instance, **kwargs):
    file_path = os.path.join(conf_settings.PATH_TO_CYBERCOACHES, instance.model_filename)  # Corrected file path

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_md5 = hashlib.md5(file_content).hexdigest()

        # Directly update the instance without triggering save()
        if instance.file_hash != file_md5:
            Cybercoach.objects.filter(pk=instance.pk).update(file_hash=file_md5)

class Subscriber(models.Model):
    REASON_CHOICES = [
        ('CFB', 'Interested in college football'),
        ('TECH', 'Interested in the technology'),
        ('OTHER', 'Other'),
    ]

    IDENTITY_CHOICES = [
        ('FAN', 'Fan of college football'),
        ('STUDENT', 'Student'),
        ('COACH_PLAYER', 'Football coach or player'),
        ('OTHER', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) # Links Djangos built-in User model
    username = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    reason_for_subscribing = models.CharField(max_length=50, choices=REASON_CHOICES, default='CFB')
    identity = models.CharField(max_length=50, choices=IDENTITY_CHOICES, default='FAN')
    email_updates = models.BooleanField(default=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"

# This model holds all of the information for each game
class Game(models.Model):
    cfbdb_game_id = models.IntegerField()
    season = models.IntegerField()
    week = models.IntegerField()
    home_team = models.CharField(max_length=50)
    away_team = models.CharField(max_length=50)
    home_money_line = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    away_money_line = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    spread = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    home_spread_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    away_spread_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    over_under = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    home_over_under_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    away_over_under_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    game_date = models.DateTimeField(null=True, blank=True)


# This model holds all of the information for each bet made by a user
class Bet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    bet_type = models.CharField(max_length=50) # 'Spread', 'Money Line', 'Over Under'
    credits_bet = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    odds = models.DecimalField(max_digits=5, decimal_places=2)
    bet_placed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')
    payout = models.IntegerField(default=0)

# This model holds all of the information for each user's credits
class UserCredit(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_credits = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, default=10000.00)
    credits_won = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, default=0)
    credits_lost = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True, default=0)
    last_updated = models.DateTimeField(auto_now=True)

# This model holds all of the information for each user's bet and the results
class BettingTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bet = models.ForeignKey(Bet, on_delete=models.SET_NULL, null=True)
    transaction_type = models.CharField(max_length=20) # 'Bet placed', 'Win', 'lose'
    credits_adjusted = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    balance_after_transaction = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    transaction_date = models.DateTimeField(auto_now_add=True)

# This model holds all of the information for each game score and when it was last updated
class GameScore(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE)
    home_team_score = models.IntegerField(default=0)
    away_team_score = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    # auto_now=True will updated this variable automatically when 'GameScore' object is updated.
    # So there is no need to update it manually in the code. 