from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from pygskin import ModelType

class Coach(models.Model):
    """Model representing a coach."""
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    latest_team = models.CharField(max_length=100, default="")
    first_year_recorded = models.IntegerField(default=2001, validators=[MinValueValidator(2001), MaxValueValidator(2023)])
    last_year_recorded = models.IntegerField(default=2001, validators=[MinValueValidator(2001), MaxValueValidator(2023)])
    # Filename of a cybercoach model of the coach, could use any of the model types (all models are stored in the same directory)
    default_cybercoach_filename = models.CharField(max_length=100, default="")
    
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

    def __str__(self):
        return f"{self.coach.first_name} {self.coach.last_name} ({self.model_type})"
    
    class Meta:
        ordering = ["coach", "model_type"]
        verbose_name = "Cybercoach"
        verbose_name_plural = "Cybercoaches"

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

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    reason_for_subscribing = models.CharField(max_length=50, choices=REASON_CHOICES, default='CFB')
    identity = models.CharField(max_length=50, choices=IDENTITY_CHOICES, default='FAN')
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"
