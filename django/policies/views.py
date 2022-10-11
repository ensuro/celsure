import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils import timezone
from decimal import Decimal

from .models import Policy
from .forms import PolicyForm
from django.contrib.auth.decorators import login_required


def get_home(request):
    policies = Policy.objects.filter(status="pending")
    return render(request, "home.html", {"policies": policies})


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
