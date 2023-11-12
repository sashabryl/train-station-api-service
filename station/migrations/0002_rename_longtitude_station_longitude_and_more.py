# Generated by Django 4.2.7 on 2023-11-07 16:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("station", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="station",
            old_name="longtitude",
            new_name="longitude",
        ),
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.UniqueConstraint(
                fields=("seat", "cargo", "journey"),
                name="unique_seat_booking",
            ),
        ),
    ]
