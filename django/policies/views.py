import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.generic.list import ListView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from celsure.motionscloud import Event, get_authenticated_session, get_inspection

from .forms import PolicyForm, PricingForm
from .models import Policy
from .serializers import PolicySerializer

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
            policy = form.save()
            web_url = policy.data["phone_inspections"][0]["web_url"]
            return render(request, "feedback/policy_created.html", {"web_url": web_url})

    else:
        form = PolicyForm()
    return render(request, "policies/new_policy.html", {"form": form})


@login_required
def price_policy(request):
    if request.method == "GET":

        form = PricingForm(request.GET)
        if form.is_valid():
            return JsonResponse(form.get_quote())

        response = JsonResponse(form.errors)
        response.status_code = 400
        return response

    return HttpResponseNotAllowed(["GET"])


class PolicyViewSet(viewsets.ModelViewSet):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer

    # metodo get que devuelve un json con los datos las primeras 10 polizas
    @action(detail=False, methods=["get"], serializer_class=None)
    def data(self, request):
        policies = self.get_queryset()
        return Response(data=[policy.data for policy in policies])

    @action(detail=False, methods=["post"], serializer_class=None)
    def webhook(self, request):
        try:
            event = Event.from_json(request.data)
        except Exception as e:
            logger.error("Bad event received on webhook: %s: %s", e, request.data)
            return Response(
                data={"error_type": "bad event"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        session = get_authenticated_session()
        inspection = get_inspection(session, event.uuid)
        policy = get_object_or_404(Policy, imei=inspection["phone_inspections"][0]["imei_number"])

        if event.imei != policy.imei:
            logger.warning(
                "Ignoring unknown policy update from motionscloud. imei=%s",
                event.imei,
            )
            return Response(data={"status": "OK"})

        policy.confirm_policy()
        policy.full_clean()
        policy.save()

        return Response(data={"status": "OK"})
