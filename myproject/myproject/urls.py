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

from pygskin_webapp import views, urls
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("pygskin_webapp/", include("pygskin_webapp.urls")),
    path("", views.index, name="index"),
    path("license/", views.license, name="license"),
    path("404/", views.handler404, name="error_404"),
    path("403/", views.handler403, name="error_403"),
    path("400/", views.handler400, name="error_400"),
    path("500/", views.generic_error, name="error_500"),
    path("error/", views.generic_error, name="error"),
    path("rate_limited/", views.rate_limit_error, name="rate_limited"),
    path("prediction/", views.prediction, name="prediction"),
    path("custom_prediction/", views.custom_prediction, name="custom_prediction"),
    path("privacy/", views.privacy, name="privacy"),
    # path("subscribed/", views.subscribed, name="subscribed"),
    path("about/", views.about, name="about"),
    path("conference_analysis/", views.conference_analysis, name="conference_analysis"),
    path("colley_matrix/", views.colley_matrix, name="colley_matrix"),
    path("coach_stats/", views.coach_stats, name="coach_stats"),
    path("cybercoach_select/", views.cybercoach_select, name="cybercoach_select"),    
    # path("signup/", views.signup_view, name="signup"),
    # path("login/", views.login_view, name="login"),
    # path("logout/", views.logout_view, name="logout"),
    # path("profile/", views.profile_view, name="profile"),
    # path("place_bets/", views.place_bets, name="place_bets"),
    # path("place_bet/", views.place_bet, name="place_bet")
]

handler400 = "pygskin_webapp.views.handler400"
handler403 = "pygskin_webapp.views.handler403"
handler404 = "pygskin_webapp.views.handler404"
handler500 = "pygskin_webapp.views.generic_error"
