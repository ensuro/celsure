from django import forms

from .models import Policy


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        widgets = {
            "model": forms.Select(attrs={"class": "form-control"}),
            "phone_color": forms.TextInput(attrs={"class": "form-control colorfield_field jscolor"}),
            "imei": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter IMEI here"}),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter phone number here"}
            ),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter email here"}),
        }
        help_texts = {
            "model": None,
            "imei": None,
            "phone_number": None,
            "phone_color": None,
            "email": None,
        }
        fields = ("model", "imei", "phone_number", "phone_color", "email")
