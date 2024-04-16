from django import forms
from django.forms import modelform_factory
from .models import Coach, Cybercoach

class CoachSelectForm(forms.Form):
    # Create a choice field populated with coach names
    coach = forms.ModelChoiceField(
        queryset=Coach.objects.all(),
        label="Select a Coach",
        empty_label="Choose a coach",
        to_field_name="id",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class CybercoachSelectForm(forms.Form):
    # Create a choice field populated with cybercoach names
    cybercoach = forms.ModelChoiceField(
        queryset=Cybercoach.objects.all(),
        label="Select a Cybercoach",
        empty_label="Choose a cybercoach",
        to_field_name="id",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
