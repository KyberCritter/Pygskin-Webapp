"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from pygskin_webapp import views

urlpatterns = [
    # path("pygskin_webapp/", include("pygskin_webapp.urls")),
    path("404/", views.handler404, name="error_404"),
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("coach/", views.coach, name="coach"),
    path("coach_list/", views.coach_list, name="coach_list"),
    path("cybercoach/", views.cybercoach, name="cybercoach"),
    path("cybercoach_list/", views.cybercoach_list, name="cybercoach_list"),
]
