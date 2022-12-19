import pytest
from requests.exceptions import HTTPError

from celsure import motionscloud


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "match_on": ["api_body", "uri_regex"],
        "allow_playback_repeats": True,
        "filter_headers": [("Authorization", "DUMMY")],
    }


@pytest.mark.vcr
@pytest.mark.block_network
@pytest.mark.django_db
def test_request_inspection():
    # m = motionscloud.MotionsCloud()
    s = motionscloud.get_authenticated_session()
    inspection = motionscloud.request_inspection(
        session=s,
        phone_status="functional",
        phone_number=1234567890,
        imei_number="123456789012345",
        brand="Apple",
    )
    assert inspection.uuid is not None
    assert inspection.phone_inspections is not None

    assert inspection.phone_inspections.__len__() == 2  # before and after repair, phone is functional
    assert inspection.phone_inspections[0]["kind"] == "before_repair"
    assert inspection.phone_inspections[0]["imei_number"] == "123456789012345"

    assert inspection.phone_inspections[1]["kind"] == "after_repaired"
    assert inspection.phone_inspections[1]["imei_number"] == "123456789012345"

    inspection = motionscloud.request_inspection(
        session=s,
        phone_status="not_functional",
        phone_number=1234567890,
        imei_number="123456789012345",
        brand="Apple",
    )
    assert inspection.uuid is not None
    assert inspection.phone_inspections is not None

    assert inspection.phone_inspections.__len__() == 1  # before repair, phone is not functional
    assert inspection.phone_inspections[0]["kind"] == "after_repaired"
    assert inspection.phone_inspections[0]["imei_number"] == "123456789012345"

    inspection = motionscloud.request_inspection(
        session=s,
        phone_status="policy_purchase",
        phone_number=1234567890,
        imei_number="123456789012345",
        brand="Apple",
    )
    assert inspection.phone_inspections.__len__() == 1
    assert inspection.phone_inspections[0]["kind"] == "policy_purchase"
    assert inspection.phone_inspections[0]["imei_number"] == "123456789012345"

    with pytest.raises(HTTPError):
        inspection = motionscloud.request_inspection(
            session=s,
            phone_status="invalid_status",
            phone_number=1234567890,
            imei_number="123456789012345",
            brand="Apple",
        )
        assert inspection.status_code == 400
