import os
import pickle

import json

import pandas as pd
import pygskin
import requests
from django.conf import settings as conf_settings
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited

from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache

# Libraries for fake bets
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
import json

from .forms import CoachSelectForm, CybercoachSelectForm, SubscriberForm, CustomScenarioForm
from .models import Cybercoach, Subscriber, Game, UserCredit, Bet, BettingTransaction

from decimal import Decimal


PATH_TO_CYBERCOACHES = conf_settings.PATH_TO_CYBERCOACHES

def get_model_type_name(model_type):
    if model_type == "DECISION_TREE":
        return "Decision Tree"
    elif model_type == "RANDOM_FOREST":
        return "Random Forest"
    elif model_type == "KNN":
        return "K-Nearest Neighbors"
    elif model_type == "LOGISTIC_REGRESSION":
        return "Logistic Regression"
    elif model_type == "MLP_NN":
        return "Multi-Layer Perceptron Neural Network"
    else:
        return model_type

@ratelimit(key='ip', rate='10/m', block=True)
def index(request):
    template = loader.get_template("pygskin_webapp/index.html")
    return HttpResponse(template.render(request=request))

def send_newsletter_signup(target_email: str):
	return requests.post(
		f"https://api.mailgun.net/v3/{conf_settings.MAILGUN_DOMAIN}/messages",
		auth=("api", conf_settings.MAILGUN_API_KEY),
		data={"from": f"Pygskin <newsletter@{conf_settings.MAILGUN_DOMAIN}>",
			"to": [target_email],
			"subject": "Welcome to the Pygskin newsletter!",
			"template": "Newsletter Confirmation",})

"""
USER ACCOUNTS TEMPORARILY DISABLED
"""
# Loads the subscriber form, checks if it is valid, and returns a subscription successful page if it is.
@ratelimit(key='ip', rate='1/m', method=ratelimit.ALL)
def subscribed(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            template = loader.get_template("pygskin_webapp/subscribed.html")
            context = {}
            return HttpResponse(template.render(context, request))
        else:
            messages.error(request, "This was an error with your submission.")
            return render(request, 'pygskin_webapp/index.html', {'subscribe_form': form})
    else:
        return redirect('index')

"""
USER ACCOUNTS TEMPORARILY DISABLED
"""
def signup_view(request):
    template = loader.get_template("pygskin_webapp/signup.html")
    context = {
        "subscribe_form": SubscriberForm(),
    }
    return HttpResponse(template.render(context, request))

"""
USER ACCOUNTS TEMPORARILY DISABLED
"""
# Loads the login page and limits the login attempts to 5
MAX_LOGIN_ATTEMPTS = 5  # Limit for login attempts
LOCKOUT_TIME = 300
@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        username = request.POST.get('username')

        # Check if the user is locked out
        lockout_key = f'lockout_{username}'
        if cache.get(lockout_key):
            messages.error(request, "This account is temporarily locked. Please try again later.")
            return render(request, 'pygskin_webapp/login.html', {'form': form})

        if form.is_valid():
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Clear the login attempt count on successful login
                cache.delete(f'login_attempts_{username}')
                auth_login(request, user)
                return redirect('profile')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            # Increment login attempts
            login_attempts_key = f'login_attempts_{username}'
            login_attempts = cache.get(login_attempts_key, 0) + 1
            cache.set(login_attempts_key, login_attempts, timeout=LOCKOUT_TIME)

            # Check if login attempts exceed the maximum limit
            if login_attempts >= MAX_LOGIN_ATTEMPTS:
                # Lock the account for LOCKOUT_TIME seconds
                cache.set(lockout_key, True, timeout=LOCKOUT_TIME)
                messages.error(request, "Too many failed login attempts. Please try again later.")
            else:
                remaining_attempts = MAX_LOGIN_ATTEMPTS - login_attempts
                messages.error(request, f"Invalid username or password. You have {remaining_attempts} attempts left.")

    form = AuthenticationForm()
    return render(request, 'pygskin_webapp/login.html', {'form': form})

"""
USER ACCOUNTS TEMPORARILY DISABLED
"""
def logout_view(request):
    logout(request)  # Log out the user
    
    # For now, we will redirect to the index page.
    # Should add in a page that notifies user of successful logout
    # and has an option to return back to the home page
    return redirect('index')

"""
USER ACCOUNTS TEMPORARILY DISABLED
"""
# Loads the profile view and all the information that the user needs to see.
def profile_view(request):
    # Make sure user is authenticated before accessing profile page
    # If not authenticated, redirect to login page
    if not request.user.is_authenticated:
        return redirect('login')

    # Loading in all user credit information
    user_credit = UserCredit.objects.get(user=request.user)
    credits_balance = user_credit.total_credits
    credits_won = user_credit.credits_won
    credits_lost = user_credit.credits_lost

    # Load in the betting transaction history for the user
    transaction_history = BettingTransaction.objects.filter(user=request.user).order_by('-transaction_date')
    active_bets = Bet.objects.filter(user=request.user, status="Pending")

    return render(request, 'pygskin_webapp/profile.html', {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'credit_balance': credits_balance,
        'credits_won': credits_won,
        'credits_lost': credits_lost,
        'transaction_history': transaction_history,
        'active_bets': active_bets,
    })

def license(request):
    template = loader.get_template("pygskin_webapp/license.html")
    context = {}
    return HttpResponse(template.render(context, request))

def privacy(request):
    template = loader.get_template("pygskin_webapp/privacy.html")
    context = {}
    return HttpResponse(template.render(context, request))

def about(request):
    template = loader.get_template("pygskin_webapp/about.html")
    context = {}
    return HttpResponse(template.render(context, request))

@ratelimit(key='ip', rate='5/m', method=ratelimit.ALL)
def conference_analysis(request):
    template = loader.get_template("pygskin_webapp/conference_analysis_2024.html")
    context = {}
    return HttpResponse(template.render(context, request))

@ratelimit(key='ip', rate='5/m', method=ratelimit.ALL)
def colley_matrix(request):
    template = loader.get_template("pygskin_webapp/colley_matrix.html")
    context = {}
    return HttpResponse(template.render(context, request))

@ratelimit(key='ip', rate='10/m', method=ratelimit.ALL)
def coach_stats(request):
    form = CoachSelectForm(request.GET)  # Initialize form with GET data
    coach_data = None
    play_dist = None
    play_dist_4th_down = None
    play_types = None
    colors = None
    coach_seasons = None

    if form.is_valid():
        selected_coach = form.cleaned_data['coach']
        # Load the cybercoach data
        cybercoach_obj = Cybercoach.objects.filter(coach=selected_coach).first()
        if cybercoach_obj:
            cybercoach_path = os.path.join(PATH_TO_CYBERCOACHES, cybercoach_obj.model_filename)
            try:
                with open(cybercoach_path, "rb") as f:
                    cybercoach = pickle.load(f)
                # Gather playcalling statistics
                play_dist = [cybercoach.play_distribution[key] for key in sorted(cybercoach.play_distribution.keys())]
                play_dist_4th_down = [cybercoach.play_distribution_by_down[4][key] for key in sorted(cybercoach.play_distribution_by_down[4].keys())]
                play_types = [pygskin.PlayType(key).name for key in sorted(cybercoach.play_distribution.keys())]
                colors = [pygskin.PLAY_TYPE_COLOR_DICT[pygskin.PlayType(key)] for key in sorted(cybercoach.play_distribution.keys())]
                # Gather coach data
                coach_data = {
                    "name": f"{selected_coach.first_name} {selected_coach.last_name}",
                    "biography": selected_coach.biography,
                    "first_year": cybercoach.coach.first_year,
                    "last_year": cybercoach.coach.last_year,
                }
                coach_seasons = cybercoach.coach.coach_dict["seasons"]
            except Exception as e:
                return redirect('error')  # Avoid exposing errors to the user

    context = {
        "coach_form": form,
        "coach_data": coach_data,
        "play_dist": play_dist,
        "play_dist_4th_down": play_dist_4th_down,
        "play_types": play_types,
        "colors": colors,
        "coach_seasons": coach_seasons,
    }
    return render(request, 'pygskin_webapp/coach_stats.html', context)

"""
USER ACCOUNTS TEMPORARILY DISABLED
"""
@ratelimit(key='ip', rate='5/m', method=ratelimit.ALL)
def place_bets(request):
    # require user to be logged in to see the place bets page
    # if user is not authenticated, redirect to signup page
    if not request.user.is_authenticated:
        return redirect('signup')

    template = loader.get_template("pygskin_webapp/place_bets.html")
    # Convert the QuerySet to a list of dictionaries
    games = Game.objects.all().values()  # or values('field1', 'field2') to include specific fields
    
    # Serialize the data to JSON
    serialized_games = json.dumps(list(games), cls=DjangoJSONEncoder)

    if not request.user.is_authenticated:
        credits_balance = 0
    else:
        # Loading in all user credit information
        user_credit = UserCredit.objects.get(user=request.user)
        credits_balance = user_credit.total_credits
        print("User Credits:", credits_balance)
    
    # context = {
    #     "games_json": serialized_games,
    #     "credit_balance": credits_balance,
    # }

    #return HttpResponse(template.render(context, request))
    return render(request, 'pygskin_webapp/place_bets.html', {
        "games_json": serialized_games,
        'credit_balance': credits_balance
    })

"""
USER ACCOUNTS TEMPORARILY DISABLED
"""
# This is the view that handles the AJAX request for placing bets
@login_required
@require_POST
def place_bet(request):
    try:
        # Get the data from the POST
        data = json.loads(request.body)
        game_id = data.get("game_id")
        bet_type = data.get("bet_type")
        credits_bet = data.get("credits_bet")
        odds = data.get("odds")

        # Ensure all fields are provided
        if game_id is None or bet_type is None or credits_bet is None or odds is None:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Convert `credits_bet` and `odds` to integers/floats after validation
        credits_bet = Decimal(credits_bet)
        odds = float(odds)

        # Get the game
        game = Game.objects.get(id=game_id)

        # Get user credits
        user_credit = UserCredit.objects.get(user=request.user)
        if credits_bet > user_credit.total_credits:
            return JsonResponse({"error": "Insufficient credits"}, status=400)

        # Deduct/update credits from users available balance 
        user_credit.total_credits -= credits_bet
        user_credit.save()

        # Create a new user bet instance
        bet = Bet.objects.create(
            user=request.user,
            game=game,
            bet_type=bet_type,
            credits_bet=credits_bet,
            odds=odds,
            #bet_placed_at=timezone.now(),
            status="Pending", # Default value until payout/loss
            payout=0, # Default value until payout/loss
        )

        return JsonResponse({"success": True, "new_balance": user_credit.total_credits})
    except Game.DoesNotExist:
        return JsonResponse({"error": "Game not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@ratelimit(key='ip', rate='10/m', method=ratelimit.ALL)
def cybercoach_select(request):
    form = CybercoachSelectForm(request.GET)  # Initialize form with GET data
    custom_scenario_form = None
    coach_name = None
    model_type = None
    first_year = None
    last_year = None
    model_accuracy = None
    opponents_by_year = None
    serialized_play_data = None

    # Redirect to default first cybercoach if no 'cybercoach' is in the GET request
    if 'cybercoach' not in request.GET or not request.GET['cybercoach']:
        # Fetch the first available cybercoach
        first_cybercoach = Cybercoach.objects.first()
        if first_cybercoach:
            # Redirect to the page with the first cybercoach selected
            return redirect(f'/cybercoach_select/?cybercoach={first_cybercoach.id}')

    if 'cybercoach' in request.GET:  # Check if 'cybercoach' is in the GET data
        if form.is_valid():
            selected_cybercoach = form.cleaned_data['cybercoach']
            if selected_cybercoach:
                cybercoach_path = os.path.join(PATH_TO_CYBERCOACHES, selected_cybercoach.model_filename)
                try:
                    with open(cybercoach_path, "rb") as f:
                        cybercoach_obj = pickle.load(f)

                    # Gather details about the coach and model
                    coach_name = f"{selected_cybercoach.coach.first_name} {selected_cybercoach.coach.last_name}"
                    model_type = selected_cybercoach.model_type
                    first_year = cybercoach_obj.coach.first_year
                    last_year = cybercoach_obj.coach.last_year
                    model_accuracy = round(cybercoach_obj.prediction_stats["accuracy"] * 100, 2)
                    custom_scenario_form = CustomScenarioForm()

                    filtered_play_data = cybercoach_obj.original_play_df[
                        (cybercoach_obj.original_play_df["season"] >= first_year) &
                        (cybercoach_obj.original_play_df["season"] <= last_year)
                    ][['drive_number', 'week', 'season']].to_dict(orient="list")  # Convert to dictionary

                    # Serialize the filtered play data
                    serialized_play_data = json.dumps(filtered_play_data)

                    # Gather opponents by year data
                    opponents_by_year = {}
                    for year in range(first_year, last_year + 1):
                        opponent_list = []
                        current_team = cybercoach_obj.coach.coach_school_dict[year]
                        for game in cybercoach_obj.coach.games_list:
                            if game.game_dict["season"] == year and game.game_dict["home_team"] == current_team and (game.game_dict["away_team"], game.game_dict["week"]) not in opponent_list:
                                opponent_list.append((game.game_dict["away_team"], game.game_dict["week"]))
                            elif game.game_dict["season"] == year and game.game_dict["away_team"] == current_team and (game.game_dict["home_team"], game.game_dict["week"]) not in opponent_list:
                                opponent_list.append((game.game_dict["home_team"], game.game_dict["week"]))
                        opponents_by_year[year] = opponent_list

                except Exception as e:
                    return redirect('error')  # Avoid exposing errors to the user

    context = {
        "cybercoach_form": form,
        "custom_scenario_form": custom_scenario_form,
        "coach_name": coach_name,
        "model_type": model_type,
        "first_year": first_year,
        "last_year": last_year,
        "model_accuracy": model_accuracy,
        "opponents_by_year": opponents_by_year,
        "play_data": serialized_play_data,
    }
    return render(request, 'pygskin_webapp/cybercoach_select.html', context)

@ratelimit(key='ip', rate='10/m', method=ratelimit.ALL)
def prediction(request):
    if request.method == 'POST':
        # Get the cybercoach ID, year, opponent, and drive from the form
        cybercoach_id = request.POST.get('cybercoach_id')
        selected_year = int(request.POST.get('year'))
        selected_opponent = request.POST.get('opponent')
        drive_number = int(request.POST.get('drive-number'))

        try:
            # Load the cybercoach object
            cybercoach_model = Cybercoach.objects.get(id=cybercoach_id)
            cybercoach_obj = pickle.load(open(os.path.join(PATH_TO_CYBERCOACHES, cybercoach_model.model_filename), "rb"))
        except Exception as e:
            return redirect('error')

        # Split the opponent and week from the opponent input
        current_opponent = selected_opponent.split(",")[0]
        selected_week = int(selected_opponent.split(",")[1])

        # Determine the current team based on the selected year
        current_team = cybercoach_obj.coach.coach_school_dict[selected_year]

        # Filter the plays for the selected drive
        drive_df = cybercoach_obj.original_play_df[
            (cybercoach_obj.original_play_df["season"] == selected_year) &
            (cybercoach_obj.original_play_df["offense"] == current_team) &
            (cybercoach_obj.original_play_df["defense"] == current_opponent) &
            (cybercoach_obj.original_play_df["week"] == selected_week) &
            (cybercoach_obj.original_play_df["drive_number"] == drive_number)
        ]

        # Call the model's prediction function and compare with the actual plays
        prediction = cybercoach_obj.call_drive(drive_df, len(drive_df) + 100).tolist()
        actual_calls = drive_df["play_call"].tolist()
        predictions_and_actual = list(zip(prediction, actual_calls))

        # Remove columns that aren't needed for display
        drive_df = drive_df.drop(columns=["id", "drive_id", "game_id"], axis=1, errors='ignore')
        drive_dict = drive_df.to_dict(orient='records')

        # Prepare the context for rendering the page
        context = {
            "selected_year": selected_year,
            "selected_week": selected_week,
            "selected_opponent": current_opponent,
            "current_team": current_team,
            "drive_dict": drive_dict,
            "predictions_and_actual": predictions_and_actual,
            "coach_name": f"{cybercoach_obj.coach.coach_dict['first_name']} {cybercoach_obj.coach.coach_dict['last_name']}",
            "first_year": cybercoach_obj.coach.first_year,
            "last_year": cybercoach_obj.coach.last_year,
            "drive_number": drive_number,
            "model_accuracy": round(cybercoach_obj.prediction_stats["accuracy"] * 100, 2),
            "model_type": get_model_type_name(cybercoach_model.model_type),
            "cybercoach_id": cybercoach_model.id,
        }

        return render(request, "pygskin_webapp/prediction.html", context)
    else:
        return redirect('index')
  
# rate limit to 3 requests per minute because machine learning models are computationally expensive
@ratelimit(key='ip', rate='3/m', method=ratelimit.ALL)
def custom_prediction(request):
    if request.method == 'POST':
        if not request.POST["cybercoach_id"]:
            return redirect('index')
        form = CustomScenarioForm(request.POST)
        if form.is_valid():
            cybercoach_model = Cybercoach.objects.get(id=request.POST["cybercoach_id"]) # not working
            try:
                cybercoach_obj = pickle.load(open(os.path.join(PATH_TO_CYBERCOACHES, cybercoach_model.model_filename), "rb"))
            except Exception as e:
                return redirect('error')    # avoid exposing the error message to the user
            
            form_data = form.cleaned_data
            # Default values for the fields not included in the form
            scenario_values = {
                'id': 0,
                'drive_id': 0,
                'game_id': 0,
                'drive_number': 1,
                'play_number': 1,
                'offense': "Placeholder Offense Team",
                'offense_conference': 'N/A',
                'offense_score': form_data['offense_score'],
                'defense': "Placeholder Defense Team",
                'home': "Placeholder Home Team",
                'away': "Placeholder Away Team",
                'defense_conference': 'N/A',
                'defense_score': form_data['defense_score'],
                'period': form_data['period'],
                'clock': {'minutes': form_data["minutes_remaining_in_quarter"], 'seconds': form_data["seconds_remaining_in_quarter"]},
                'offense_timeouts': form_data['offense_timeouts'],
                'defense_timeouts': form_data['defense_timeouts'],
                'yard_line': form_data['yard_line'],
                'yards_to_goal': 100 - form_data['yard_line'],
                'down': form_data['down'],
                'distance': form_data['distance'],
                'yards_gained': 0,
                'scoring': False,
                'play_type': "Rush", # must have a value, but it doesn't matter
                'play_text': 'N/A',
                'ppa': 0.0,
                'wallclock': '2024-05-14T00:00:00.000Z',
                'week': 1,
                'season': 2024,
                'seconds_remaining': form_data["minutes_remaining_in_quarter"] * 60 + form_data["seconds_remaining_in_quarter"],
                'score_diff': form_data['offense_score'] - form_data['defense_score'],
                'passing_yards_per_attempt': form_data['passing_yards_per_attempt'],
                'rushing_yards_per_attempt': form_data['rushing_yards_per_attempt'],
                'play_call': 5, # must have a value, but it doesn't matter
            }
            
            # Create a single-item DataFrame
            scenario_df = pd.DataFrame([scenario_values])

            # Prediction using the model
            prediction = cybercoach_obj.call_drive(scenario_df, 1)

            context = {
                "drive_dict": scenario_df.to_dict(orient='records'),
                "coach_name": cybercoach_obj.coach.coach_dict["first_name"] + " " + cybercoach_obj.coach.coach_dict["last_name"],
                "first_year": cybercoach_obj.coach.first_year,
                "last_year": cybercoach_obj.coach.last_year,
                "coach_seasons": cybercoach_obj.coach.coach_dict["seasons"],
                "model_accuracy": round(cybercoach_obj.prediction_stats["accuracy"] * 100, 2),
                "model_type": get_model_type_name(cybercoach_model.model_type),
                "cybercoach_id": cybercoach_model.id,
                "prediction": prediction,
            }
            
            return render(request, "pygskin_webapp/custom_prediction.html", context)
        else:
            return redirect('index')
    else:
        return redirect('index')

def handler400(request, *args, **argv):
    return HttpResponse(render(request, "400.html"), status=400)

def handler403(request, exception=None, *args, **argv):
    if isinstance(exception, Ratelimited):
        return rate_limit_error(request, *args, **argv)
    return HttpResponse(render(request, "403.html"), status=403)

def handler404(request, *args, **argv):
    return HttpResponse(render(request, "404.html"), status=404)

def generic_error(request, *args, **argv):
    return HttpResponse(render(request, "error.html"))

def rate_limit_error(request, *args, **argv):
    return HttpResponse(render(request, "pygskin_webapp/rate_limited.html"))
