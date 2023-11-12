from django.core.exceptions import ValidationError
from django.test import TestCase

from station.models import Station


class StationModelTest(TestCase):
    def test_longitude_latitude_validation(self):
        with self.assertRaises(ValidationError):
            Station.objects.create(
                name="station", longitude=361, latitude=32.4
            )
