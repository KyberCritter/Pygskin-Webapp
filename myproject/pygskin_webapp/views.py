from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import pygskin

import os
import pickle

def index(request):
    return HttpResponse("Hello, world. You're at the Pygskin index.")

def cybercoach_selection(request):
    # Cybercoach access page
    template = loader.get_template("pygskin_webapp/cybercoach_selection.html")

    # TODO: find a better way to store the paths
    cybercoach_paths = {
        "Kalen Deboer": {
            "decision_tree": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Kalen_Deboer_decision_tree.cybercoach"),
            "neural_network": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Kalen_Deboer_neural_network.cybercoach"),
            "k_nearest_neighbors": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Kalen_Deboer_k_nearest_neighbors.cybercoach"),
            "logistic_regression": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Kalen_Deboer_logistic_regression.cybercoach"),
            "random_forest": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Kalen_Deboer_random_forest.cybercoach"),
        },
        "Deion Sanders": {
            "decision_tree": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Deion_Sanders_decision_tree.cybercoach"),
            "neural_network": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Deion_Sanders_neural_network.cybercoach"),
            "k_nearest_neighbors": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Deion_Sanders_k_nearest_neighbors.cybercoach"),
            "logistic_regression": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Deion_Sanders_logistic_regression.cybercoach"),
            "random_forest": os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Deion_Sanders_random_forest.cybercoach"),
        }
    }
    # cybercoach_path = os.path.join(os.path.curdir, "pygskin_webapp/cybercoaches/Kalen_Deboer_decision_tree.cybercoach")
    # cybercoach = pickle.load(open(cybercoach_path, "rb"))
    # print(os.path.curdir)
    # cybercoach = pickle.load(open(cybercoach_path, "rb"))
    # context["coach_name"] = cybercoach.coach.coach_dict["first_name"] + " " + cybercoach.coach.coach_dict["last_name"]
    # # context["coach_dict"] = cybercoach.coach.coach_dict
    # context["coach_seasons"] = cybercoach.coach.coach_dict["seasons"]
    context = {
        "cybercoach_paths": cybercoach_paths
    }
    return HttpResponse(template.render(context, request))

def cybercoach_render(request, cybercoach_path):
    # Cybercoach render page
    template = loader.get_template("pygskin_webapp/cybercoach.html")
    context = {
        # empty for now
    }
    cybercoach = pickle.load(open(cybercoach_path, "rb"))
    context["coach_name"] = cybercoach.coach.coach_dict["first_name"] + " " + cybercoach.coach.coach_dict["last_name"]
    # context["coach_dict"] = cybercoach.coach.coach_dict
    context["coach_seasons"] = cybercoach.coach.coach_dict["seasons"]
    return HttpResponse(template.render(context, request))
