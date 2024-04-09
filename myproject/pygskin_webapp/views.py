import os
import pickle

import pygskin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import RequestContext, loader


def index(request):
    return HttpResponse(render(request, "pygskin_webapp/index.html"))

# TODO: find a better way to store the paths
cybercoach_paths = {
    "Kalen DeBoer": {
        "decision_tree": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Kalen_Deboer_decision_tree.cybercoach"),
        "random_forest": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Kalen_Deboer_random_forest.cybercoach"),
        "k_nearest_neighbors": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Kalen_Deboer_k_nearest_neighbors.cybercoach"),
        "logistic_regression": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Kalen_Deboer_logistic_regression.cybercoach"),
        "neural_network": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Kalen_Deboer_neural_network.cybercoach"),
    },
    "Deion Sanders": {
        "decision_tree": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Deion_Sanders_decision_tree.cybercoach"),
        "random_forest": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Deion_Sanders_random_forest.cybercoach"),
        "k_nearest_neighbors": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Deion_Sanders_k_nearest_neighbors.cybercoach"),
        "logistic_regression": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Deion_Sanders_logistic_regression.cybercoach"),
        "neural_network": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Deion_Sanders_neural_network.cybercoach"),
    },
    "Biff Poggi": {
        "decision_tree": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Biff_Poggi_decision_tree.cybercoach"),
        "random_forest": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Biff_Poggi_random_forest.cybercoach"),
        "k_nearest_neighbors": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Biff_Poggi_k_nearest_neighbors.cybercoach"),
        "logistic_regression": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Biff_Poggi_logistic_regression.cybercoach"),
        "neural_network": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Biff_Poggi_neural_network.cybercoach"),
    }
}

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

        # Prepare context data for rendering
        context = {
            "coach_name": cybercoach.coach.coach_dict["first_name"] + " " + cybercoach.coach.coach_dict["last_name"],
            "coach_seasons": cybercoach.coach.coach_dict["seasons"],
        }

        # Render and return the template with context
        return render(request, "pygskin_webapp/cybercoach.html", context)

    else:
        # Redirect or show an error for non-POST requests
        # Adjust the redirect path as necessary
        return redirect('index')

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

        # Prepare context data for rendering
        context = {
            "coach_name": cybercoach.coach.coach_dict["first_name"] + " " + cybercoach.coach.coach_dict["last_name"],
            "coach_seasons": cybercoach.coach.coach_dict["seasons"],
        }

        # Render and return the template with context
        return render(request, "pygskin_webapp/coach.html", context)

    else:
        # Redirect or show an error for non-POST requests
        # Adjust the redirect path as necessary
        return redirect('index')

def handler404(request, *args, **argv):
    return HttpResponse(render(request, "pygskin_webapp/404.html"), status=404)
