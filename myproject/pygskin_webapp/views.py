import os
import pickle

import pygskin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import RequestContext, loader
import pandas as pd


def index(request):
    template = loader.get_template("pygskin_webapp/index.html")
    context = {
        "cybercoach_paths": cybercoach_paths
    }
    return HttpResponse(template.render(context, request))

def license(request):
    template = loader.get_template("pygskin_webapp/license.html")
    context = {}
    return HttpResponse(template.render(context, request))

# TODO: find a better way to store the paths
path_to_cybercoaches = os.path.join(os.path.curdir, "myproject/pygskin_webapp/cybercoaches/")
cybercoach_paths = {
    "Kalen DeBoer": {
        "decision_tree": os.path.join(os.path.curdir, path_to_cybercoaches, "Kalen_Deboer_decision_tree.cybercoach"),
        "random_forest": os.path.join(os.path.curdir, path_to_cybercoaches, "Kalen_Deboer_random_forest.cybercoach"),
        "k_nearest_neighbors": os.path.join(os.path.curdir, path_to_cybercoaches, "Kalen_Deboer_k_nearest_neighbors.cybercoach"),
        "logistic_regression": os.path.join(os.path.curdir, path_to_cybercoaches, "Kalen_Deboer_logistic_regression.cybercoach"),
        "neural_network": os.path.join(os.path.curdir, path_to_cybercoaches, "Kalen_Deboer_neural_network.cybercoach"),
    },
    "Deion Sanders": {
        "decision_tree": os.path.join(os.path.curdir, path_to_cybercoaches, "Deion_Sanders_decision_tree.cybercoach"),
        "random_forest": os.path.join(os.path.curdir, path_to_cybercoaches, "Deion_Sanders_random_forest.cybercoach"),
        "k_nearest_neighbors": os.path.join(os.path.curdir, path_to_cybercoaches, "Deion_Sanders_k_nearest_neighbors.cybercoach"),
        "logistic_regression": os.path.join(os.path.curdir, path_to_cybercoaches, "Deion_Sanders_logistic_regression.cybercoach"),
        "neural_network": os.path.join(os.path.curdir, path_to_cybercoaches, "Deion_Sanders_neural_network.cybercoach"),
    },
    "Biff Poggi": {
        "decision_tree": os.path.join(os.path.curdir, path_to_cybercoaches, "Biff_Poggi_decision_tree.cybercoach"),
        "random_forest": os.path.join(os.path.curdir, path_to_cybercoaches, "Biff_Poggi_random_forest.cybercoach"),
        "k_nearest_neighbors": os.path.join(os.path.curdir, path_to_cybercoaches, "Biff_Poggi_k_nearest_neighbors.cybercoach"),
        "logistic_regression": os.path.join(os.path.curdir, path_to_cybercoaches, "Biff_Poggi_logistic_regression.cybercoach"),
        "neural_network": os.path.join(os.path.curdir, path_to_cybercoaches, "Biff_Poggi_neural_network.cybercoach"),
    }
}

def coach_list(request):
    # Cybercoach access page
    template = loader.get_template("pygskin_webapp/coach_list.html")
    context = {
        "cybercoach_paths": cybercoach_paths
    }
    return HttpResponse(template.render(context, request))

def coach(request):
    # Only proceed if this is a POST request
    if request.method == 'POST':
        # Extract the selected coach and model type from the POST request
        selected_coach = request.POST.get('coach')

        # Construct the cybercoach_path based on the selections
        # This part assumes you have a way to determine the path from the selected coach and model type
        if selected_coach in cybercoach_paths:
            cybercoach_path = cybercoach_paths[selected_coach][[x for x in cybercoach_paths[selected_coach].keys()][0]]
        else:
            # Handle the case where the path does not exist for the selected options
            return HttpResponse("Selected model path does not exist.", status=404)

        # Load the cybercoach from the path
        try:
            cybercoach = pickle.load(open(cybercoach_path, "rb"))
        except Exception as e:
            return HttpResponse(f"Error loading model: {e}", status=500)
        
        # Gather playcalling statistics
        play_dist = [value for value in cybercoach.play_distribution.values()]
        play_types = [pygskin.PlayType(key).name for key in cybercoach.play_distribution.keys()]
        colors = [pygskin.PLAY_TYPE_COLOR_DICT[pygskin.PlayType(key)] for key in cybercoach.play_distribution.keys()]

        # Prepare context data for rendering
        context = {
            "coach_name": cybercoach.coach.coach_dict["first_name"] + " " + cybercoach.coach.coach_dict["last_name"],
            "first_year": cybercoach.coach.first_year,
            "last_year": cybercoach.coach.last_year,
            "coach_seasons": cybercoach.coach.coach_dict["seasons"],
            "play_dist": play_dist,
            "play_types": play_types,
            "colors": colors,
        }

        # Render and return the template with context
        return render(request, "pygskin_webapp/coach.html", context)

    else:
        # Redirect or show an error for non-POST requests
        # Adjust the redirect path as necessary
        return redirect('index')

def cybercoach_list(request):
    # Cybercoach access page
    template = loader.get_template("pygskin_webapp/cybercoach_list.html")
    context = {
        "cybercoach_paths": cybercoach_paths
    }
    return HttpResponse(template.render(context, request))

def cybercoach(request):
    # Only proceed if this is a POST request
    if request.method == 'POST':
        # Extract the selected coach and model type from the POST request
        selected_coach = request.POST.get('coach')
        selected_model_type = request.POST.get('model_type')

        # Construct the cybercoach_path based on the selections
        # This part assumes you have a way to determine the path from the selected coach and model type
        if selected_coach in cybercoach_paths and selected_model_type in cybercoach_paths[selected_coach]:
            cybercoach_path = cybercoach_paths[selected_coach][selected_model_type]
        else:
            # Handle the case where the path does not exist for the selected options
            return HttpResponse("Selected model path does not exist.", status=404)

        # Load the cybercoach from the path
        try:
            cybercoach = pickle.load(open(cybercoach_path, "rb"))
        except Exception as e:
            return HttpResponse(f"Error loading model: {e}", status=500)

        first_year = cybercoach.coach.first_year
        last_year = cybercoach.coach.last_year
        opponents_by_year = {}
        for year in range(first_year, last_year + 1):
            opponent_list = []
            current_team = cybercoach.coach.coach_school_dict[year]
            for game in cybercoach.coach.games_list:
                if game.game_dict["season"] == year and game.game_dict["home_team"] == current_team and (game.game_dict["away_team"], game.game_dict["week"]) not in opponent_list:
                    opponent_list.append((game.game_dict["away_team"], game.game_dict["week"]))
                    # opponent_list.append(game.game_dict["away_team"])
                elif game.game_dict["season"] == year and game.game_dict["away_team"] == current_team and (game.game_dict["home_team"], game.game_dict["week"]) not in opponent_list:
                    opponent_list.append((game.game_dict["home_team"], game.game_dict["week"]))
                    # opponent_list.append(game.game_dict["home_team"])
            # self.opponent_combo_box.addItems([f"{opponent}, Week {week}" for opponent, week in opponent_list])
            opponents_by_year[year] = opponent_list

        # Prepare context data for rendering
        context = {
            "coach_name": cybercoach.coach.coach_dict["first_name"] + " " + cybercoach.coach.coach_dict["last_name"],
            "first_year": first_year,
            "last_year": last_year,
            "coach_seasons": cybercoach.coach.coach_dict["seasons"],
            "opponents_by_year": opponents_by_year,
            "cybercoach_path": cybercoach_path,
        }
        request.session['cybercoach_path'] = cybercoach_path

        # Render and return the template with context
        return render(request, "pygskin_webapp/cybercoach.html", context)

    else:
        # Redirect or show an error for non-POST requests
        # Adjust the redirect path as necessary
        return redirect('index')
    
def cybercoach_results(request):
    if request.method == 'POST':
        # Extract the selected coach and model type from the POST request
        # selected_coach = request.POST.get('selected_coach')
        # selected_model_type = request.POST.get('model_type')
        selected_opponent = request.POST.get('opponent')
        selected_year = int(request.POST.get('year'))

        cybercoach_obj = pickle.load(open(request.session['cybercoach_path'], "rb"))
        current_team = cybercoach_obj.coach.coach_school_dict[selected_year]
        current_opponent = selected_opponent.split(",")[0]
        current_week = int(selected_opponent.split(",")[1])
        game_dict = cybercoach_obj.original_play_df[(cybercoach_obj.original_play_df["season"] == selected_year) & (cybercoach_obj.original_play_df["offense"] == current_team) & (cybercoach_obj.original_play_df["defense"] == current_opponent) & (cybercoach_obj.original_play_df["week"] == current_week)].to_dict()

        context = {
            "selected_opponent": current_opponent,
            "selected_week": current_week,
            "selected_year": selected_year,
            "current_team": current_team,
            "df_columns": cybercoach_obj.original_play_df.columns,
            "game_dict": game_dict,
            "drive_numbers": set(game_dict["drive_number"].values()),
        }
        request.session['selected_opponent'] = current_opponent
        request.session['current_week'] = current_week
        request.session['selected_year'] = selected_year
        request.session['current_team'] = current_team
        request.session['df_columns'] = list(cybercoach_obj.original_play_df.columns)
        request.session['game_dict'] = game_dict
        request.session['drive_numbers'] = list(set(game_dict["drive_number"].values()))

        # Render and return the template with context
        return render(request, "pygskin_webapp/cybercoach_results.html", context)

def prediction(request):
    # game_dict = request.session['game_dict']
    cybercoach_obj = pickle.load(open(request.session['cybercoach_path'], "rb"))
    selected_opponent = request.session['selected_opponent']
    current_team = request.session['current_team']
    current_opponent = selected_opponent.split(",")[0]
    current_week = request.session['current_week']
    selected_year = request.session['selected_year']
    drive_dict = cybercoach_obj.original_play_df[(cybercoach_obj.original_play_df["season"] == selected_year) & (cybercoach_obj.original_play_df["offense"] == current_team) & (cybercoach_obj.original_play_df["defense"] == current_opponent) & (cybercoach_obj.original_play_df["week"] == current_week) & (cybercoach_obj.original_play_df["drive_number"] == int(request.POST.get('drive')))].to_dict()
    # drive_number = request.POST.get('drive')
    request.session['drive_dict'] = drive_dict
    prediction = cybercoach_obj.call_drive(pd.DataFrame(drive_dict), len(drive_dict))
    context = {
        "selected_opponent": selected_opponent,
        "selected_week": current_week,
        "selected_year": selected_year,
        "current_team": current_team,
        "drive_dict": drive_dict,
        "df_columns": cybercoach_obj.original_play_df.columns,
        "prediction": prediction,
    }
    return render(request, "pygskin_webapp/prediction.html",context)

def handler404(request, *args, **argv):
    return HttpResponse(render(request, "pygskin_webapp/404.html"), status=404)
