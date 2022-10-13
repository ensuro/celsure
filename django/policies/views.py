import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils import timezone
from django.views.generic.list import ListView

from .forms import PolicyForm
from .models import Policy


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
            post = form.save(commit=False)
            post.premium = Decimal(10)
            post.payout = Decimal(100)
            post.expiration = timezone.now() + datetime.timedelta(days=int(10))
            post.status = "pending"
            post.save()
            return render(request, "feedback/policy_created.html")

    else:
        form = PolicyForm()
    return render(request, "policies/new_policy.html", {"form": form})
