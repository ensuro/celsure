import csv

from django.core.management.base import BaseCommand

from policies.models import Brand, Model

from . import PrintMixin


class Command(PrintMixin, BaseCommand):
    help = "Loads the brands and models"

    def handle(self, *args, **options):
        with open("policies/data/PhoneFixPricelist.csv") as file:
            reader = csv.reader(file)
            next(reader)  # Advance past the header

            for row in reader:
                brand, _ = Brand.objects.get_or_create(code=row[0], name=row[1])
                model_code = row[1] + "-" + row[2]
                model = Model(brand=brand, name=row[2], code=model_code, fix_price=row[3])
                model.save()
                self._print(f"Model {model} - Created")
