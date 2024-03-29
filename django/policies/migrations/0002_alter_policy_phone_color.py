# Generated by Django 3.2.16 on 2022-10-13 16:00

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("policies", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="policy",
            name="phone_color",
            field=colorfield.fields.ColorField(
                default="#FFFFFF",
                help_text="Select the color of the phone cover",
                image_field=None,
                max_length=18,
                samples=[
                    ("#FFFFFF", "white"),
                    ("#000000", "black"),
                    ("#808080", "gray"),
                    "#000000black",
                    ("#FF0000", "red"),
                    ("#FFC0CB", "pink"),
                    ("#000080", "navy"),
                    ("#008080", "teal"),
                    ("#00FF00", "green"),
                ],
            ),
        ),
    ]
