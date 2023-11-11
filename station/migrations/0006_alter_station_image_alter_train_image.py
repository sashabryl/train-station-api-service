# Generated by Django 4.2.7 on 2023-11-11 15:57

from django.db import migrations, models
import station.models


class Migration(migrations.Migration):
    dependencies = [
        ("station", "0005_alter_station_latitude_alter_station_longitude"),
    ]

    operations = [
        migrations.AlterField(
            model_name="station",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to=station.models.station_image_file_path
            ),
        ),
        migrations.AlterField(
            model_name="train",
            name="image",
            field=models.ImageField(
                blank=True, null=True, upload_to=station.models.train_image_file_path
            ),
        ),
    ]
