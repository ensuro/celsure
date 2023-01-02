from django.apps import AppConfig
from ensuro.contracts import register_contract_path

register_contract_path()


class PoliciesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "policies"
