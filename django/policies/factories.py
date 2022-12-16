import factory
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
