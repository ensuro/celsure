import datetime
from dataclasses import dataclass

import requests
from django.conf import settings
from django.utils import timezone
from oauth2_provider.models import AccessToken


@dataclass
class Inspection:
    uuid: str
    phone_inspections: str

    @classmethod
    def from_json(cls, data):
        ret = cls(
            uuid=data["uuid"],
            phone_inspections=data["phone_inspections"],
        )
        ret._data = data
        return ret


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


class MotionsCloud:
    token = None

    def __init__(self):
        self.token = authenticate()

    def request_inspection(self, phone_status, phone_number, imei_number, brand, description=""):
        if self.token.is_expired():
            self.token = authenticate()

        response = requests.post(
            f"{settings.MOTIONSCLOUD_API_URL}/phone_inspections/case",
            headers={
                "Authorization": f"Bearer {self.token.token}",
            },
            json={
                "phone_status": phone_status,
                "phone_number": phone_number,
                "imei_number": imei_number,
                "brand": brand,
                "description": description,
            },
        )
        response.raise_for_status()
        return Inspection.from_json(response.json())

    def get_inspection(self, uuid):
        if self.token.is_expired():
            self.token = authenticate()

        response = requests.get(
            f"{settings.MOTIONSCLOUD_API_URL}/phone_inspections/assessment?uuid={uuid}",
            headers={
                "Authorization": f"Bearer {self.token.token}",
            },
        )
        response.raise_for_status()
        return Inspection.from_json(response.json())
