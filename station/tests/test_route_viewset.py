from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from station.models import Station, Route
from station.serializers import RouteListSerializer, RouteDetailSerializer


ROUTE_URL = reverse("train-station:route-list")


def sample_station(**params):
    defaults = {
        "name": "Sample vokzal",
        "latitude": 10.15,
        "longitude": 32.14,
    }
    defaults.update(params)

    return Station.objects.get_or_create(**defaults)[0]


def sample_route(
    source_n: str = "first", destination_n: str = "second", **params
):
    defaults = {
        "source": sample_station(name=source_n),
        "destination": sample_station(name=destination_n),
        "distance": 100,
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def get_detail_url(route_id: int):
    return reverse("train-station:route-detail", args=[route_id])


class PublicRouteApiTests(TestCase):
    """Check that users don't have too much access"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="feaioj@fjaeio.com", password="324ewae1!"
        )
        self.client.force_authenticate(self.user)

    def test_create_method_forbidden(self):
        payload = {
            "source": sample_station(name="first"),
            "destination": sample_station(name="second"),
            "distance": 100,
        }
        res = self.client.post(ROUTE_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_method_forbidden(self):
        payload = {
            "source": sample_station(name="third"),
            "destination": sample_station(name="fourth"),
            "distance": 200,
        }
        sample_route()
        res = self.client.put(get_detail_url(1), data=payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_forbidden(self):
        sample_route()
        res = self.client.patch(get_detail_url(1), data={"distance": 300})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_method_forbidden(self):
        sample_route()
        res = self.client.delete(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
