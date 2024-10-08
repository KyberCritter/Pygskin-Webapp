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

from .forms import CoachSelectForm, CybercoachSelectForm, SubscriberForm, CustomScenarioForm
from .models import Cybercoach

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
    context = {
        "coach_form": CoachSelectForm(),
        "cybercoach_form": CybercoachSelectForm(),
        "subscribe_form": SubscriberForm(),
    }
    return HttpResponse(template.render(context, request))

def send_newsletter_signup(target_email: str):
	return requests.post(
		f"https://api.mailgun.net/v3/{conf_settings.MAILGUN_DOMAIN}/messages",
		auth=("api", conf_settings.MAILGUN_API_KEY),
		data={"from": f"Pygskin <newsletter@{conf_settings.MAILGUN_DOMAIN}>",
			"to": [target_email],
			"subject": "Welcome to the Pygskin newsletter!",
			"template": "Newsletter Confirmation",})

@ratelimit(key='ip', rate='1/m', method=ratelimit.ALL)
def subscribed(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            model = form.save()
            template = loader.get_template("pygskin_webapp/subscribed.html")
            context = {}
            return HttpResponse(template.render(context, request))
        else:
            return redirect('index')
    else:
        return redirect('index')

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

@ratelimit(key='ip', rate='5/m', method=ratelimit.ALL)
def coach(request):
    # Only proceed if this is a POST request
    if request.method == 'POST':
        form = CoachSelectForm(request.POST)
        
        if form.is_valid():
            # Extract the selected coach and model type from the POST request
            coach = form.cleaned_data.get('coach')
            # Load the cybercoach from the path
            cybercoach_obj = Cybercoach.objects.filter(coach=coach).first()
            if cybercoach_obj is None:
                return redirect('error')    # avoid exposing the error message to the user
            cybercoach_path = os.path.join(PATH_TO_CYBERCOACHES, cybercoach_obj.model_filename)
            try:
                cybercoach = pickle.load(open(cybercoach_path, "rb"))
            except Exception as e:                
                return redirect('error')    # avoid exposing the error message to the user

            # Gather playcalling statistics
            play_dist = [cybercoach.play_distribution[key] for key in sorted(cybercoach.play_distribution.keys())]
            # play_dist_1st_down = [value for value in cybercoach.play_distribution_by_down[1].values()]
            # play_dist_2nd_down = [value for value in cybercoach.play_distribution_by_down[2].values()]
            # play_dist_3rd_down = [value for value in cybercoach.play_distribution_by_down[3].values()]
            play_dist_4th_down = [cybercoach.play_distribution_by_down[4][key] for key in sorted(cybercoach.play_distribution_by_down[4].keys())]
            play_types = [pygskin.PlayType(key).name for key in sorted(cybercoach.play_distribution.keys())]
            colors = [pygskin.PLAY_TYPE_COLOR_DICT[pygskin.PlayType(key)] for key in sorted(cybercoach.play_distribution.keys())]

            # Prepare context data for rendering
            context = {
                "coach_name": f"{coach.first_name} {coach.last_name}",
                "first_year": cybercoach.coach.first_year,
                "last_year": cybercoach.coach.last_year,
                "coach_seasons": cybercoach.coach.coach_dict["seasons"],
                "play_dist": play_dist,
                "play_types": play_types,
                "colors": colors,
                "form": form,
                # "play_dist_1st_down": play_dist_1st_down,
                # "play_dist_2nd_down": play_dist_2nd_down,
                # "play_dist_3rd_down": play_dist_3rd_down,
                "play_dist_4th_down": play_dist_4th_down,
                "coach_bio": coach.biography,
            }

            # Render and return the template with context
            return render(request, "pygskin_webapp/coach.html", context)
        
        else:
            # Redirect or show an error for invalid form data
            return redirect('index')
    else:
        # Redirect or show an error for non-POST requests
        # Adjust the redirect path as necessary
        return redirect('index')

@ratelimit(key='ip', rate='10/m', method=ratelimit.ALL)
def coach_stats(request):
    form = CoachSelectForm(request.GET)  # Initialize form with GET data
    coach_data = None
    play_dist = None
    play_dist_4th_down = None
    play_types = None
    colors = None
    coach_seasons = None

    if 'coach' in request.GET:  # Check if 'coach' is in the GET data
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

@ratelimit(key='ip', rate='5/m', method=ratelimit.ALL)
def cybercoach(request):
    # Only proceed if this is a POST request
    if request.method == 'POST':
        form = CybercoachSelectForm(request.POST)

        if form.is_valid():
            # Extract the selected cybercoach from the POST request
            cybercoach_model = form.cleaned_data.get('cybercoach')
            # Load the cybercoach from the path
            if cybercoach_model is None:
                return redirect('error')    # avoid exposing the error message to the user
            cybercoach_path = os.path.join(PATH_TO_CYBERCOACHES, cybercoach_model.model_filename)
            try:
                cybercoach_obj = pickle.load(open(cybercoach_path, "rb"))
            except Exception as e:
                return redirect('error')    # avoid exposing the error message to the user

            first_year = cybercoach_obj.coach.first_year
            last_year = cybercoach_obj.coach.last_year
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
                
            # Prepare context data for rendering
            context = {
                "coach_name": cybercoach_obj.coach.coach_dict["first_name"] + " " + cybercoach_obj.coach.coach_dict["last_name"],
                "first_year": first_year,
                "last_year": last_year,
                "coach_seasons": cybercoach_obj.coach.coach_dict["seasons"],
                "opponents_by_year": opponents_by_year,
                "current_team": cybercoach_obj.coach.coach_school_dict[cybercoach_obj.coach.first_year],
                "model_accuracy": round(cybercoach_obj.prediction_stats["accuracy"] * 100, 2),
                "cybercoach_id": cybercoach_model.id,
                "model_type": get_model_type_name(cybercoach_model.model_type),
                "custom_scenario_form": CustomScenarioForm()  # Add the form to the context
            }
            for key, value in context.items():
                if key == "custom_scenario_form":
                    continue
                request.session[key] = value

            # Render and return the template with context
            return render(request, "pygskin_webapp/cybercoach.html", context)
        else:
            # Redirect or show an error for invalid form data
            return redirect('index')
    else:
        # Redirect or show an error for non-POST requests
        return redirect('index')

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

@ratelimit(key='ip', rate='5/m', method=ratelimit.ALL)
def drive_select(request):
    # select a drive from the cybercoach
    if request.method == 'POST':
        if "cybercoach_id" not in request.session:
            return redirect('index')
        if not request.session["cybercoach_id"]:
            return redirect('index')
        cybercoach_model = Cybercoach.objects.get(id=request.session["cybercoach_id"])
        try:
            cybercoach_obj = pickle.load(open(os.path.join(PATH_TO_CYBERCOACHES, cybercoach_model.model_filename), "rb"))
        except Exception as e:
            return redirect('error')    # avoid exposing the error message to the user

        # Extract the selected coach and model type from the POST request
        selected_opponent = request.POST.get('opponent')
        selected_year = int(request.POST.get('year'))

        current_team = cybercoach_obj.coach.coach_school_dict[selected_year]
        current_opponent = selected_opponent.split(",")[0]
        selected_week = int(selected_opponent.split(",")[1])
        game_dict = cybercoach_obj.original_play_df[(cybercoach_obj.original_play_df["season"] == selected_year) & (cybercoach_obj.original_play_df["offense"] == current_team) & (cybercoach_obj.original_play_df["defense"] == current_opponent) & (cybercoach_obj.original_play_df["week"] == selected_week)].to_dict()

        context = {
            "selected_year": selected_year,
            "selected_week": selected_week,
            "selected_opponent": current_opponent,
            "current_team": current_team,
            "game_dict": game_dict,
            "drive_numbers": list(set(game_dict["drive_number"].values())),
            "coach_name": cybercoach_obj.coach.coach_dict["first_name"] + " " + cybercoach_obj.coach.coach_dict["last_name"],
            "first_year": cybercoach_obj.coach.first_year,
            "last_year": cybercoach_obj.coach.last_year,
            "coach_seasons": cybercoach_obj.coach.coach_dict["seasons"],
            "model_accuracy": round(cybercoach_obj.prediction_stats["accuracy"] * 100, 2),
            "model_type": get_model_type_name(cybercoach_model.model_type),
            "cybercoach_id": cybercoach_model.id,
        }
        for key, value in context.items():
            request.session[key] = value
    
        return render(request, "pygskin_webapp/drive_select.html", context)
    else:
        # Redirect or show an error for non-POST requests
        return redirect('index')

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

    
@ratelimit(key='ip', rate='3/m', method=ratelimit.ALL)  # rate limit to 3 requests per minute because machine learning models are computationally expensive
def custom_prediction(request):
    if request.method == 'POST':
        if not request.session.get("cybercoach_id"):
            return redirect('index')
        form = CustomScenarioForm(request.POST)
        if form.is_valid():
            cybercoach_model = Cybercoach.objects.get(id=request.session["cybercoach_id"])
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
