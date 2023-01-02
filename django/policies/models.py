import logging

import ensuro.wrappers as wrappers
from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from django.db import models
from django_fsm import FSMField, transition
from django_fsm_log.decorators import fsm_log_by
from environs import Env
from ethproto.wadray import _W
from ethproto.wrappers import get_provider
from phonenumber_field.modelfields import PhoneNumberField

from celsure import motionscloud
from policies.ethutils import _A
from policies.quote import get_quote

env = Env()

logger = logging.getLogger()


# Took from https://github.com/mmcloughlin/luhn/blob/master/luhn.py
def luhn_checksum(string):
    """
    Compute the Luhn checksum for the provided string of digits. Note this
    assumes the check digit is in place.
    """
    digits = list(map(int, string))
    odd_sum = sum(digits[-1::-2])
    even_sum = sum([sum(divmod(2 * d, 10)) for d in digits[-2::-2]])
    return (odd_sum + even_sum) % 10


def luhn_verify(string):
    """
    Check if the provided string of digits satisfies the Luhn checksum.
    >>> verify('356938035643809')
    True
    >>> verify('534618613411236')
    False
    """
    return luhn_checksum(string) == 0


def validate_imei(value):
    if len(value) != 15 or not value.isdigit():
        raise ValidationError(
            "%(value)s is not a valid IMEI, must be 15 digits",
            params={"value": value},
        )
    if not luhn_verify(value):
        raise ValidationError(
            "%(value)s is not a valid IMEI - check the number again",
            params={"value": value},
        )


class Brand(models.Model):
    code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Model(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="models")
    code = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50)
    fix_price = models.DecimalField(decimal_places=2, max_digits=12)

    def __str__(self):
        return f"{self.brand.name} - {self.name}"


STATUS_CHOICES = (
    ("pending", "Pending"),  # Initial status, not yet confirmed by the user + payment of the premium
    ("confirmed", "Confirmed"),  # Confirmed by the user
    ("active", "Active"),  # Policy created on Ensuro side
    ("expired", "Expired"),  # Policy expired, no longer claimable
    ("claimed", "Claim process started"),
    ("on_repair", "Delivered to repair center"),
    ("claim_validated", "Claim validated"),
    ("refunded", "Refunded"),  # Payout released on Ensuro side
    ("cancelled", "Cancelled"),
)


class Policy(models.Model):
    COLOR_PALETTE = [
        ("#FFFFFF", "white"),
        ("#000000", "black"),
        ("#808080", "gray"),
        ("#000000" "black"),
        ("#FF0000", "red"),
        ("#FFC0CB", "pink"),
        ("#000080", "navy"),
        ("#008080", "teal"),
        ("#00FF00", "green"),
    ]

    model = models.ForeignKey(
        Model,
        on_delete=models.PROTECT,
        related_name="policies",
        help_text="Choose a brand/model from the supported ones",
    )
    imei = models.CharField(
        max_length=15, validators=[validate_imei], help_text="15 digit IMEI number that identifies the phone"
    )
    phone_number = PhoneNumberField(
        blank=False, help_text="Phone number of the user, it will be used to confirm the data with the user"
    )
    email = models.EmailField(max_length=254, blank=True)
    phone_color = ColorField(samples=COLOR_PALETTE, help_text="Select the color of the phone cover")
    premium = models.DecimalField(decimal_places=2, max_digits=12)
    payout = models.DecimalField(decimal_places=2, max_digits=12)

    expiration = models.DateTimeField()
    status = FSMField(default="pending")

    quote = models.JSONField(null=True)
    data = models.JSONField(default=dict)

    @fsm_log_by
    @transition(field=status, source="pending", target="inspection_requested")
    def inspection_request(self):
        session = motionscloud.get_authenticated_session()
        inspection = motionscloud.request_inspection(
            session, "policy_purchase", self.phone_number.as_e164, self.imei, self.model.brand.name
        )

        self.data.update(inspection)
        return

    @fsm_log_by
    @transition(field=status, source="inspection_requested", target="inspection_confirmed")
    def confirm_inspection(self):
        return

    @fsm_log_by
    @transition(field=status, source="inspection_confirmed", target="policy_created")
    def create_policy(self):
        get_provider()
        quote = get_quote(model=self.model, expiration=self.expiration, signed=True)
        eth_rm = wrappers.SignedQuoteRiskModule.connect(env.str("CELSURE_RM_ADDRESS"))
        customer = env.str("CUSTOMER_ADDRESS")
        from_address = env.str("REPLICATOR_ADDRESS")

        with eth_rm.as_(from_address):
            receipt = eth_rm.new_policy_(
                _A(self.model.fix_price),
                _A(quote["premium"]) if quote["premium"] is not None else None,
                _W(quote["loss_prob"]),
                quote["expiration"],
                customer,
                quote["data_hash"],
                quote["signature"]["r"],
                quote["signature"]["vs"],
                quote["valid_until"],
            )

        self.data["policy"] = {"data_hash": quote["data_hash"], "receipt": receipt}
        logger.info(f"Policy created, receipt: {receipt}")
        return
