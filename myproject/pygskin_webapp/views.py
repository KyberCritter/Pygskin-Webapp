import os
import pickle

import pandas as pd
import pygskin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import RequestContext, loader

from .forms import CoachSelectForm, CybercoachSelectForm
from .models import Coach, Cybercoach


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

def index(request):
    template = loader.get_template("pygskin_webapp/index.html")
    context = {
        "coach_form": CoachSelectForm(),
        "cybercoach_form": CybercoachSelectForm(),
    }
    return HttpResponse(template.render(context, request))

def license(request):
    template = loader.get_template("pygskin_webapp/license.html")
    context = {}
    return HttpResponse(template.render(context, request))

# TODO: find a better way to store the paths
path_to_cybercoaches = "/app/myproject/pygskin_webapp/cybercoaches"

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
            cybercoach_path = os.path.join(path_to_cybercoaches, cybercoach_obj.model_filename)
            try:
                cybercoach = pickle.load(open(cybercoach_path, "rb"))
            except Exception as e:
                return redirect('error')    # avoid exposing the error message to the user

            # Gather playcalling statistics
            play_dist = [value for value in cybercoach.play_distribution.values()]
            play_types = [pygskin.PlayType(key).name for key in cybercoach.play_distribution.keys()]
            colors = [pygskin.PLAY_TYPE_COLOR_DICT[pygskin.PlayType(key)] for key in cybercoach.play_distribution.keys()]

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

def cybercoach(request):
    # Only proceed if this is a POST request
    if request.method == 'POST':
        form = CybercoachSelectForm(request.POST)

        if form.is_valid():
            # Extract the selected cybercoach from the POST request
            cybercoach_model = form.cleaned_data.get('cybercoach')
            # Load the cybercoach from the path
            if cybercoach_model is None:
                print("Cybercoach model is None")
                return redirect('error')    # avoid exposing the error message to the user
            cybercoach_path = os.path.join(path_to_cybercoaches, cybercoach_model.model_filename)
            try:
                cybercoach_obj = pickle.load(open(cybercoach_path, "rb"))
            except Exception as e:
                print(e)
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
            }
            for key, value in context.items():
                request.session[key] = value

            # Render and return the template with context
            return render(request, "pygskin_webapp/cybercoach.html", context)
        else:
            # Redirect or show an error for invalid form data
            return redirect('index')
    else:
        # Redirect or show an error for non-POST requests
        return redirect('index')

def drive_select(request):
    # select a drive from the cybercoach
    if request.method == 'POST':
        if "cybercoach_id" not in request.session:
            return redirect('index')
        if not request.session["cybercoach_id"]:
            return redirect('index')
        cybercoach_model = Cybercoach.objects.get(id=request.session["cybercoach_id"])
        try:
            cybercoach_obj = pickle.load(open(os.path.join(path_to_cybercoaches, cybercoach_model.model_filename), "rb"))
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

def prediction(request):
    if request.method == 'POST':
        if not request.session["cybercoach_id"]:
            return redirect('index')
        cybercoach_model = Cybercoach.objects.get(id=request.session["cybercoach_id"])
        try:
            cybercoach_obj = pickle.load(open(os.path.join(path_to_cybercoaches, cybercoach_model.model_filename), "rb"))
        except Exception as e:
            return redirect('error')    # avoid exposing the error message to the user

        selected_opponent = request.session['selected_opponent']
        current_team = request.session['current_team']
        current_opponent = selected_opponent.split(",")[0]
        selected_week = request.session['selected_week']
        selected_year = request.session['selected_year']
        try:
            drive_number = int(request.POST.get('drive-number'))
        except Exception as e:
            return redirect('error')    # avoid exposing the error message to the user

        drive_df = cybercoach_obj.original_play_df[(cybercoach_obj.original_play_df["season"] == selected_year) & (cybercoach_obj.original_play_df["offense"] == current_team) & (cybercoach_obj.original_play_df["defense"] == current_opponent) & (cybercoach_obj.original_play_df["week"] == selected_week) & (cybercoach_obj.original_play_df["drive_number"] == drive_number)]
        drive_dict = drive_df.to_dict(orient='records')
        prediction = cybercoach_obj.call_drive(drive_df, len(drive_df) + 1).tolist()
        actual_calls = drive_df["play_call"].tolist()
        predictions_and_actual = list(zip(prediction, actual_calls))

        context = {
            "selected_year": selected_year,
            "selected_week": selected_week,
            "selected_opponent": current_opponent,
            "current_team": current_team,
            "drive_dict": drive_dict,
            "predictions_and_actual": predictions_and_actual,
            "coach_name": cybercoach_obj.coach.coach_dict["first_name"] + " " + cybercoach_obj.coach.coach_dict["last_name"],
            "first_year": cybercoach_obj.coach.first_year,
            "last_year": cybercoach_obj.coach.last_year,
            "coach_seasons": cybercoach_obj.coach.coach_dict["seasons"],
            "drive_number": drive_number,
            "model_accuracy": round(cybercoach_obj.prediction_stats["accuracy"] * 100, 2),
            "model_type": get_model_type_name(cybercoach_model.model_type),
            "cybercoach_id": cybercoach_model.id,
        }
        for key, value in context.items():
            request.session[key] = value
        
        return render(request, "pygskin_webapp/prediction.html", context)
    else:
        # Redirect or show an error for non-POST requests
        return redirect('index')

def handler400(request, *args, **argv):
    return HttpResponse(render(request, "pygskin_webapp/400.html"), status=400)

def handler403(request, *args, **argv):
    return HttpResponse(render(request, "pygskin_webapp/403.html"), status=403)

def handler404(request, *args, **argv):
    return HttpResponse(render(request, "pygskin_webapp/404.html"), status=404)

def generic_error(request, *args, **argv):
    return HttpResponse(render(request, "pygskin_webapp/error.html"))
