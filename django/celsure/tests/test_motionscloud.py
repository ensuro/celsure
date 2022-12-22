import pytest
import responses
from django.conf import settings
from django.urls import reverse
from responses import matchers

from policies.factories import Model as ModelFactory


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "match_on": ["api_body", "uri_regex"],
        "allow_playback_repeats": True,
        "filter_post_data_parameters": [("client_id", "ID_TEST"), ("client_secret", "SECRET_TEST")],
        "filter_headers": [("Authorization", "DUMMY")],
    }


@pytest.fixture
def settings_pricing(settings):
    settings.DYNAMIC_PRICING_URL = "https://example.org/quote"
    settings.DYNAMIC_PRICING_API_KEY = "insecure"


@pytest.fixture
def settings_motionscloud(settings):
    settings.MOTIONSCLOUD_BASE_URL = "https://example.org/motionscloud"
    settings.MOTIONSCLOUD_API_URL = "https://example.org/motionscloud/api"
    settings.MOTIONSCLOUD_CLIENT_ID = "fake_client"
    settings.MOTIONSCLOUD_CLIENT_SECRET = "fake_secret"


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


def create_motionscloud_api_response():
    inspection = {
        "uuid": "1af220a3-8a30-4dfc-b120-19006608643e",
        "phone_inspections": [
            {
                "uuid": "fake_uuid",
                "imei_number": "AA-BBBBBB-CCCCCC-D",
                "kind": "policy_purchase",
                "web_url": "https://ensuro-qa.motionscloud.com/phone_inspections/fake_uuid/guidelines",
                "treatment": None,
                "treatment_options": [],
            }
        ],
    }
    responses.post(
        url=settings.MOTIONSCLOUD_API_URL + "/phone_inspections/case",
        match=[
            matchers.header_matcher({"Authorization": "Bearer insecure"}),
        ],
        json=inspection,
    )
    return inspection


def create_auth_motionscloud_response():
    auth = {"access_token": "insecure", "token_type": "Bearer", "expires_in": 3600, "created_at": 1671632939}
    responses.post(
        url=settings.MOTIONSCLOUD_BASE_URL + "/oauth/token",
        json=auth,
    )
    return auth


@pytest.mark.vcr
@pytest.mark.django_db
def test_request_inspection(client, settings_pricing, settings_motionscloud):
    model = ModelFactory()
    # Request to the dynamic pricing api
    expiration = "2022-12-14T16:57:08.727839+00:00"
    create_quote_response(model, expiration)
    create_auth_motionscloud_response()
    inspection = create_motionscloud_api_response()

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

    assert inspection["uuid"] is not None
    assert inspection["phone_inspections"] is not None

    assert inspection["phone_inspections"].__len__() == 1  # only policy_purchase
    assert inspection["phone_inspections"][0]["kind"] == "policy_purchase"
    assert inspection["phone_inspections"][0]["imei_number"] == "AA-BBBBBB-CCCCCC-D"
