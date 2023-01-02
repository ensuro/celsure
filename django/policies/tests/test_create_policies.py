import pytest

from policies import factories


@pytest.fixture
def create_policy_mock(mocker):
    return mocker.patch("policies.models.Policy.create_policy")


@pytest.fixture
def request_inspection(mocker):
    return mocker.patch("celsure.motionscloud.request_inspection")


@pytest.fixture
def get_authenticated_session(mocker):
    return mocker.patch("celsure.motionscloud.get_authenticated_session")


@pytest.mark.django_db
def test_bad_state_transition():
    wrong_policy = factories.Policy(status="wrong_status")
    with pytest.raises(Exception, match="Can't switch from state"):
        wrong_policy.inspection_request()


@pytest.mark.django_db
def test_create_policy(request_inspection, get_authenticated_session):
    inspection = {
        "uuid": "fake_uuid",
        "phone_inspections": [
            {
                "uuid": "diferent_uuid",
                "imei_number": "123456789012345",
                "kind": "policy_purchase",
                "web_url": "https://ensuro-qa.motionscloud.com/phone_inspections/diferent_uuid/guidelines",
                "treatment": None,
                "treatment_options": [],
            }
        ],
    }
    request_inspection.return_value = inspection

    policy = factories.Policy(imei="123456789012345")
    policy.inspection_request()

    assert policy.status == "inspection_requested"
    assert policy.data == inspection
    assert policy.imei == "123456789012345"

    policy.confirm_inspection()
    assert policy.status == "inspection_confirmed"
