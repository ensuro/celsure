import requests
from django.conf import settings

_session = requests.Session()


def get_quote(model, expiration, data=None, signed=False):
    assert settings.DYNAMIC_PRICING_URL is not None

    response = _session.post(
        settings.DYNAMIC_PRICING_URL,
        headers={"X-Api-Key": settings.DYNAMIC_PRICING_API_KEY},
        params=None if signed else {"unsigned": True},
        json={
            "payout": str(model.fix_price),
            "expiration": expiration.isoformat(),
            "data": {"brand": model.brand.code, "model": model.code, "fix_price": str(model.fix_price)},
        },
    )

    response.raise_for_status()
    return response.json()
