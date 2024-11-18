from django import forms
from django.core.validators import validate_email
from django.forms import ModelForm, TextInput, modelform_factory

# Brooks imported libraries
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.contrib.auth.hashers import make_password

from .models import Coach, Cybercoach, Subscriber, UserCredit


class CoachSelectForm(forms.Form):
    # Create a choice field populated with coach names
    coach = forms.ModelChoiceField(
        queryset=Coach.objects.all(),
        empty_label="Choose a coach",
        to_field_name="id",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class CybercoachSelectForm(forms.Form):
    # Create a choice field populated with cybercoach names
    cybercoach = forms.ModelChoiceField(
        queryset=Cybercoach.objects.all(),
        label="SELECT A CYBERCOACH",
        empty_label="Choose a cybercoach",
        to_field_name="id",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

# This form will create a new subscriber and add in a new user to the DB
class SubscriberForm(ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password",
        required=True
    )

    age_confirmation = forms.BooleanField(
        label="I confirm that I am at least 13 years old.",
        required=True,
        error_messages={'required': "You must confirm that you are at least 13 years old."}
    )

    email_updates = forms.BooleanField(
        label="Sign up for email updates",
        required=False,
        initial=True
    )
    
    class Meta:
        model = Subscriber
        fields = ['username', 'first_name', 'last_name', 'email', 'reason_for_subscribing', 'identity', 'age_confirmation', 'email_updates']
        widgets = {
            'username': TextInput(attrs={'class': 'form-control'}),
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'}),
            'reason_for_subscribing': forms.Select(attrs={'class': 'form-control'}),
            'identity': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'identity': 'Best describes me'
        }

    # Function to make sure that each email submitted is unique
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Subscriber.objects.filter(email=email).exists() or User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email has already been subscribed.")
        return email
    
    # Function to make sure that each username submitted is unique
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
    
    # Saves the subscriber, creates a user, and give the user credits
    def save(self, commit=True):
        # Create a User instance for authentication
        user = User.objects.create(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            password=make_password(self.cleaned_data['password']),  # Hash the password
        )

        # Put the user in the UserCredit table and give them credits
        UserCredit.objects.create(user=user)
        
        # Link the subscriber to the newly created user
        subscriber = super().save(commit=False)
        subscriber.user = user

        if commit:
            subscriber.save()

        return subscriber


class CustomScenarioForm(forms.Form):
    TIMEOUTS_CHOICES = [(i, str(i)) for i in range(0, 4)]
    QUARTER_CHOICES = [(i, str(i)) for i in range(1, 5)]
    DOWN_CHOICES = [(i, str(i)) for i in range(1, 5)]

    yard_line = forms.IntegerField(
        label="YARD LINE",
        initial=25,
        min_value=0,
        max_value=100,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        # help_text="0 is the offense's end zone and 100 is the defense's end zone."
    )
    down = forms.ChoiceField(
        label="DOWN",
        choices=DOWN_CHOICES,
        initial=1,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    distance = forms.IntegerField(
        label="DISTANCE TO 1ST",
        min_value=1,
        max_value=99,
        initial=10,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    period = forms.ChoiceField(
        label="QUARTER",
        choices=QUARTER_CHOICES,
        initial=1,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    minutes_remaining_in_quarter = forms.IntegerField(
        label="MINUTES REMAINING",
        min_value=0,
        max_value=15,
        initial=15,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    seconds_remaining_in_quarter = forms.IntegerField(
        label="SECONDS REMAINING",
        min_value=0,
        max_value=59,
        initial=0,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    offense_score = forms.IntegerField(
        label="SCORE",
        min_value=0,
        initial=0,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    defense_score = forms.IntegerField(
        label="SCORE",
        min_value=0,
        initial=0,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    offense_timeouts = forms.ChoiceField(
        label="TIMEOUTS",
        choices=TIMEOUTS_CHOICES,
        initial=3,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    defense_timeouts = forms.ChoiceField(
        label="TIMEOUTS",
        choices=TIMEOUTS_CHOICES,
        initial=3,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    rushing_yards_per_attempt = forms.FloatField(
        label="RUSH YARDS/ATTEMPT",
        min_value=-100,
        max_value=100,
        initial=3,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    passing_yards_per_attempt = forms.FloatField(
        label="PASS YARDS/ATTEMPT",
        min_value=-100,
        max_value=100,
        initial=5,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def clean_time_remaining(self):
        time_remaining_in_quarter = self.cleaned_data['time_remaining']
        if time_remaining_in_quarter.minute > 15 or time_remaining_in_quarter.second > 59:
            raise forms.ValidationError("Invalid time remaining. Must be within a quarter duration.")
        return time_remaining_in_quarter
