import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from . import models


class Brand(DjangoModelFactory):
    class Meta:
        model = models.Brand
        django_get_or_create = ("code", "name")

    code = factory.Sequence(lambda n: f"Brand-{n}")
    name = factory.Sequence(lambda n: f"Brand test {n}")


class Model(DjangoModelFactory):
    class Meta:
        model = models.Model

    brand = factory.SubFactory(Brand)
    code = factory.Sequence(lambda n: f"Model-{n}")
    name = factory.Sequence(lambda n: f"Model test {n}")
    fix_price = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)


class Policy(DjangoModelFactory):
    class Meta:
        model = models.Policy

    model = factory.SubFactory(Model)
    imei = factory.Sequence(lambda n: n)
    phone_number = factory.Sequence(lambda n: f"+1{n}")
    email = factory.Faker("email")
    phone_color = factory.Sequence(lambda n: f"Color-{n}")

    payout = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    premium = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    expiration = factory.Faker("future_datetime", tzinfo=timezone.get_current_timezone())
    status = "pending"
    quote = None
    data = {}
