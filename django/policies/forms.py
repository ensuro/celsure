from django import forms
from django.shortcuts import get_object_or_404

from .models import Model, Policy
from .quote import get_quote


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
        ret.payout = ret.model.fix_price
        ret.status = "pending"

        quote = get_quote(ret.payout, ret.expiration, signed=False)
        ret.quote = quote
        ret.premium = quote["premium"]

        if commit:
            ret.save()

        return ret


class PricingForm(forms.Form):

    model = forms.CharField()
    expiration = forms.DateTimeField()

    def clean_model(self):
        model_code = self.cleaned_data["model"]
        return get_object_or_404(Model, code=model_code)

    def get_quote(self):
        return get_quote(self.cleaned_data["model"].fix_price, self.cleaned_data["expiration"], signed=False)
