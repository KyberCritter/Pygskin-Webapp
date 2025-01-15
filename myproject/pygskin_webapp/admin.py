from django.contrib import admin
from .models import *

@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'latest_team', 'first_year_recorded', 'last_year_recorded',)
    search_fields = ('first_name', 'last_name', 'latest_team', 'first_year_recorded', 'last_year_recorded', 'biography',)
    list_filter = ('latest_team', 'first_year_recorded', 'last_year_recorded',)

@admin.register(Cybercoach)
class CybercoachAdmin(admin.ModelAdmin):
    list_display = ('coach', 'model_type', 'model_filename',)
    readonly_fields = ('file_hash',)
    search_fields = ('coach', 'model_type', 'model_filename',)
    list_filter = ('coach', 'model_type',)

admin.site.register(Subscriber)
admin.site.register(Game)
admin.site.register(Bet)
admin.site.register(UserCredit)
admin.site.register(BettingTransaction)
admin.site.register(GameScore)
