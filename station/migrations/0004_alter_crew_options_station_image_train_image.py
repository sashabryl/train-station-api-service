# Generated by Django 4.2.7 on 2023-11-09 18:07

from django.db import migrations, models
import station.models


class Migration(migrations.Migration):
    dependencies = [
        ("station", "0003_route_description_route_unique_route"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="crew",
            options={"ordering": ["last_name", "first_name"]},
        ),
        migrations.AddField(
            model_name="station",
            name="image",
            field=models.ImageField(
                null=True, upload_to=station.models.station_image_file_path
            ),
        ),
        migrations.AddField(
            model_name="train",
            name="image",
            field=models.ImageField(
                null=True, upload_to=station.models.train_image_file_path
            ),
        ),
    ]
