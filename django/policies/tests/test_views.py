import pytest
import responses
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlencode
from pytest_django.asserts import assertRedirects, assertTemplateUsed
from responses import matchers

from policies.factories import Model as ModelFactory
from policies.models import Policy


@pytest.fixture
@pytest.mark.django_db
def logged_in_user(django_user_model, client):
    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)
    return user


def test_not_logged_in_redirect_to_login(client):
    # Cant see policy_list if not logged in
    resp = client.get("", follow=True)
    assertRedirects(resp, "/accounts/login/?next=/")
    assertTemplateUsed(resp, "registration/login.html")


@pytest.mark.django_db
def test_login_and_render_policy_list(client, django_user_model):
    # Cant see policy_list if not logged in
    response = client.get("", follow=True)
    assertTemplateUsed(response, "registration/login.html")

    username = "user1"
    password = "bar"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.force_login(user)

    response = client.get("", follow=True)
    assertTemplateUsed(response, "policies/policy_list.html")


@pytest.mark.django_db
def test_new_policy_form_render(client, logged_in_user):
    response = client.get(reverse("new_policy"), follow=True)
    assert response.status_code == 200
    assertTemplateUsed(response, "policies/new_policy.html")


@pytest.fixture
def settings_pricing(settings):
    settings.DYNAMIC_PRICING_URL = "https://example.org/quote"
    settings.DYNAMIC_PRICING_API_KEY = "insecure"


def create_quote_response(model, expiration):
    """Create a quote and register a response for it in responses"""
    quote = {
        "contract_address": "0xa9f43F43D3BcA4392Fa47B4c727395DeB85c2748",
        "data_hash": "0x4f6b70369bbb026a94b641bc47c263dda3b1fd8feb99f9eff08f0b98f5211695",
        "expiration": 1672176967,
        "loss_prob": "0.0113",
        "premium": "18.687507",
        "premium_details": {"minimum_premium": "18.687507"},
        "quote_id": "22a4c094-8dce-40dc-b933-b107d857e619",
        "valid_until": 1671130141,
    }
    responses.post(
        url=settings.DYNAMIC_PRICING_URL,
        match=[
            matchers.query_param_matcher({"unsigned": True}),
            matchers.json_params_matcher(
                {
                    "payout": str(model.fix_price),
                    "expiration": expiration,
                    "data": {
                        "brand": model.brand.code,
                        "model": model.code,
                        "fix_price": str(model.fix_price),
                    },
                }
            ),
            matchers.header_matcher({"X-Api-Key": "insecure"}),
        ],
        json=quote,
    )
    return quote


@pytest.mark.django_db
def test_new_policy_form_post(client, logged_in_user, settings_pricing):
    model = ModelFactory()
    # Request to the dynamic pricing api
    expiration = "2022-12-14T16:57:08.727839+00:00"
    quote = create_quote_response(model, expiration)

    response = client.post(
        reverse("new_policy"),
        {
            "model": model.code,
            "phone_color": "#000000",
            "imei": "356938035643809",
            "phone_number": "+541112345678",
            "expiration": expiration,
        },
        follow=True,
    )
    assert response.status_code == 200
    assertTemplateUsed(response, "feedback/policy_created.html")

    assert Policy.objects.count() == 1
    policy = Policy.objects.get()
    assert policy.payout == model.fix_price
    assert policy.quote == quote


@pytest.mark.django_db
def test_price_policy(client, logged_in_user, settings_pricing):
    expiration = "2022-12-14T16:57:08.727839+00:00"
    model = ModelFactory()
    quote = create_quote_response(model, expiration)

    response = client.get(
        "%s?%s" % (reverse("price_policy"), urlencode({"model": model.code, "expiration": expiration}))
    )
    assert response.json() == quote


@pytest.mark.django_db
def test_price_policy_missing_args(client, logged_in_user):
    response = client.get(reverse("price_policy"))
    assert response.status_code == 400
    assert response.json() == {
        "expiration": ["This field is required."],
        "model": ["This field is required."],
    }
