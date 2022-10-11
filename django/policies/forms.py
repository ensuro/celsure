from django import forms
from .models import Policy


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = ("model", "imei", "phone_number", "phone_color", "email")
