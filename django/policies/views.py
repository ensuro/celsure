import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView

from .forms import PolicyForm, PricingForm
from .models import Policy

logger = logging.getLogger(__name__)


class PoliciesListView(LoginRequiredMixin, ListView):

    model = Policy
    paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context


@login_required
def new_policy(request):
    if request.method == "POST":
        form = PolicyForm(request.POST)

        if form.is_valid():
            form.save()
            return render(request, "feedback/policy_created.html")

    else:
        form = PolicyForm()
    return render(request, "policies/new_policy.html", {"form": form})


# @login_required
@csrf_exempt
def price_policy(request):
    if request.method == "GET":

        form = PricingForm(request.GET)
        if form.is_valid():
            logger.info(form.cleaned_data)

            return JsonResponse(form.get_quote())

        response = JsonResponse(form.errors)
        response.status_code = 400
        return response

    return HttpResponseNotAllowed(["POST"])
