from decimal import Decimal

from django import forms

from .models import Policy


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        widgets = {
            "model": forms.Select(
                attrs={"class": "form-control form-select selectpicker", "data-live-search": "true"}
            ),
            "phone_color": forms.TextInput(attrs={"class": "form-control colorfield_field jscolor"}),
            "imei": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter IMEI here"}),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter phone number here"}
            ),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter email here"}),
            "expiration": forms.DateTimeInput(attrs={"class": "form-control", "type": "date"}),
        }
        fields = ("model", "imei", "phone_number", "phone_color", "email", "expiration")

    def save(self, commit=True) -> Policy:
        ret: Policy = super().save(commit=False)
        ret.premium = Decimal(10)  # TODO: get premium from api
        ret.payout = ret.model.fix_price
        ret.status = "pending"

        if commit:
            ret.save()

        return ret
