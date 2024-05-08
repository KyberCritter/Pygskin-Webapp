from django import forms
from django.forms import modelform_factory, ModelForm, TextInput
from .models import Coach, Cybercoach, Subscriber

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

class SubscriberForm(ModelForm):
    age_confirmation = forms.BooleanField(
        label="I confirm that I am at least 13 years old.",
        required=True,
        error_messages={'required': "You must confirm that you are at least 13 years old."}
    )
    
    class Meta:
        model = Subscriber
        fields = ['first_name', 'last_name', 'email', 'reason_for_subscribing', 'identity', 'age_confirmation']
        widgets = {
            'first_name': TextInput(attrs={'class': 'form-control'}),
            'last_name': TextInput(attrs={'class': 'form-control'}),
            'email': TextInput(attrs={'class': 'form-control'}),
            'reason_for_subscribing': forms.Select(attrs={'class': 'form-control'}),
            'identity': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'identity': 'Best describes me'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Subscriber.objects.filter(email=email).exists():
            raise forms.ValidationError("This email has already been subscribed.")
        return email
