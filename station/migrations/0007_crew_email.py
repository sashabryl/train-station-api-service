# Generated by Django 4.2.7 on 2023-11-12 07:22

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("station", "0006_alter_station_image_alter_train_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="crew",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]