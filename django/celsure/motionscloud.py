import datetime
from dataclasses import dataclass

import requests
from django.conf import settings
from django.utils import timezone
from oauth2_provider.models import AccessToken

TOKEN = None


@dataclass
class Event:
    uuid: str
    imei: str
    phone_inspections: str

    @classmethod
    def from_json(cls, data):
        return cls(
            uuid=data["data"]["uuid"],
            imei=data["data"]["phone_inspections"][0]["imei_number"],
            phone_inspections=data["data"]["phone_inspections"],
        )


def create_access_token(token):
    return AccessToken(
        token=token["access_token"],
        expires=timezone.now() + datetime.timedelta(seconds=token["expires_in"]),
        created=token["created_at"],
    )


def authenticate():
    response = requests.post(
        f"{settings.MOTIONSCLOUD_BASE_URL}/oauth/token",
        headers={"Content-Type": "application/json"},
        json={
            "grant_type": "client_credentials",
            "client_id": f"{settings.MOTIONSCLOUD_CLIENT_ID}",
            "client_secret": f"{settings.MOTIONSCLOUD_CLIENT_SECRET}",
        },
    )

    return create_access_token(response.json())


def get_authenticated_session():
    global TOKEN
    if not TOKEN or TOKEN.is_expired():
        TOKEN = authenticate()

    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {TOKEN}"})
    return session


def request_inspection(session, phone_status, phone_number, imei_number, brand, description=""):
    response = session.post(
        f"{settings.MOTIONSCLOUD_API_URL}/phone_inspections/case",
        json={
            "phone_status": phone_status,
            "phone_number": phone_number,
            "imei_number": imei_number,
            "brand": brand,
            "description": description,
        },
    )
    response.raise_for_status()
    return response.json()


def get_inspection(session, uuid):
    response = session.get(
        f"{settings.MOTIONSCLOUD_API_URL}/phone_inspections/assessment?uuid={uuid}",
    )
    response.raise_for_status()
    return response.json()
