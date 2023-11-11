import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from station.models import Station
from station.serializers import TrainListSerializer, StationListSerializer, StationDetailSerializer

STATION_URL = reverse("train_station:station-list")


def sample_station(**params):
    defaults = {
        "name": "Sample vokzal",
        "latitude": 10.15,
        "longitude": 32.14,
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


def get_detail_url(station_id: int):
    return reverse("train_station:station-detail", args=[station_id])


class PublicStationApiTests(TestCase):
    """Here authenticated and anonymous users have the same level of access"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="test@gnail.com", password="!@eawr@3"
        )
        self.client.force_authenticate(self.user)

    def test_list_retrieve_methods_allowed(self):
        sample_station()
        res = self.client.get(STATION_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        Station.objects.first().delete()

    """
    There is something creepy about it. See what happens here.
    Something similar happens with the api: when creating a new instance,
    at api/train-station/stations/ that instance will appear only after
    rerunning the server. How to fix it? 
    """
    def test_list_returns_correct_data(self):
        station_one = sample_station(name="first")
        print(Station.objects.all())
        station_two = sample_station(name="second")
        print(Station.objects.all())
        res = self.client.get(STATION_URL)
        print(res.data)
        serializer = StationListSerializer([station_one, station_two], many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_returns_correct_data(self):
        station = sample_station()
        serializer = StationDetailSerializer(station, many=False)
        res = self.client.get(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filtering_by_name(self):
        station_one = sample_station(name="station1")
        station_two = sample_station(name="station2")
        station_three = sample_station(name="restaurant")

        res = self.client.get(STATION_URL, data={"name": "station"})
        serializer = StationListSerializer(
            [station_one, station_two], many=True
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_method_forbidden(self):
        payload = {
            "name": "station",
            "latitude": 23.5,
            "longitude": 10.3,
        }
        res = self.client.post(STATION_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_method_forbidden(self):
        payload = {
            "name": "station",
            "latitude": 23.5,
            "longitude": 10.3,
        }
        sample_station()
        res = self.client.put(get_detail_url(1), data=payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_forbidden(self):
        sample_station()
        res = self.client.patch(get_detail_url(1), data={"name": "updated"})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_method_forbidden(self):
        sample_station()
        res = self.client.delete(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminStationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="BAueai32!"
        )
        self.client.force_authenticate(self.user)

    def test_create_allowed(self):
        payload = {
            "name": "station",
            "latitude": 23.5,
            "longitude": 10.3,
        }
        res = self.client.post(STATION_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_partial_update_allowed(self):
        sample_station()
        payload = {
            "name": "station",
            "latitude": 23.5,
            "longitude": 10.3,
        }
        res = self.client.put(get_detail_url(1), data=payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.patch(get_detail_url(1), data={"name": "new"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_allowed(self):
        sample_station()
        res = self.client.delete(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
