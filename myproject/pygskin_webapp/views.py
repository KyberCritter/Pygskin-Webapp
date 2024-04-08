from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import pygskin

def index(request):
    return HttpResponse("Hello, world. You're at the Pygskin index.")

def cybercoach(request):
    # Cybercoach access page
    template = loader.get_template("pygskin_webapp/cybercoach.html")
    context = {
        # empty for now
    }
    return HttpResponse(template.render(context, request))
