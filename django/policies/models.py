from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from colorfield.fields import ColorField


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
    return (luhn_checksum(string) == 0)


def validate_imei(value):
    if len(value) != 15 or not value.isdigit():
        raise ValidationError(
            '%(value)s is not a valid IMEI, must be 15 digits',
            params={'value': value},
        )
    if not luhn_verify(value):
        raise ValidationError(
            '%(value)s is not a valid IMEI - check the number again',
            params={'value': value},
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
    ("confirmed", "Confirmed"),   # Confirmed by the user
    ("active", "Active"),  # Policy created on Ensuro side
    ("expired", "Expired"),  # Policy expired, no longer claimable
    ("claimed", "Claim process started"),
    ("on_repair", "Delivered to repair center"),
    ("claim_validated", "Claim validated"),
    ("refunded", "Refunded"),  # Payout released on Ensuro side
    ("cancelled", "Cancelled"),
)


class Policy(models.Model):
    model = models.ForeignKey(
        Model, on_delete=models.PROTECT, related_name="policies",
        help_text="Choose a brand/model from the supported ones"
    )
    imei = models.CharField(
        max_length=15, validators=[validate_imei],
        help_text="15 digit IMEI number that identifies the phone"
    )
    phone_number = PhoneNumberField(
        blank=False,
        help_text="Phone number of the user, it will be used to confirm the data with the user"
    )
    email = models.EmailField(max_length=254, blank=True)
    phone_color = ColorField(help_text="Select the color of the phone cover")
    premium = models.DecimalField(decimal_places=2, max_digits=12)
    payout = models.DecimalField(decimal_places=2, max_digits=12)

    expiration = models.DateTimeField()

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending",
        help_text="Tracks the status of the policy"
    )
    # TODO: ensuro_id and/or hash and/or quote


class PolicyActivity(models.Model):
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name="activities")
    status_from = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
    )
    status_to = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
    )
    timestamp = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    params = models.JSONField(default=dict)
