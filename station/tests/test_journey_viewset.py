import datetime
import json
import random
import uuid

from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from station.models import TrainType, Train, Station, Route, Crew, Journey
from station.serializers import JourneyListSerializer, JourneyDetailSerializer


JOURNEY_URL = reverse("train-station:journey-list")


def serialize_datetime(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")


def sample_train_type():
    return TrainType.objects.create(name=f"express{uuid.uuid4()}")


def sample_train(**params):
    defaults = {
        "name": "Lincorn",
        "cargo_num": 10,
        "places_in_cargo": 15,
        "train_type": sample_train_type(),
    }
    defaults.update(params)

    return Train.objects.create(**defaults)


def sample_station(**params):
    defaults = {
        "name": f"Sample vokzal{uuid.uuid4()}",
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
        "distance": random.randint(1, 10000),
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_crew(**params):
    defaults = {"first_name": "joe", "last_name": "worker"}
    defaults.update(params)
    return Crew.objects.create(**defaults)


def sample_journey(**params):
    with override_settings(USE_TZ=False):
        defaults = {
            "route": sample_route(),
            "train": sample_train(),
            "departure_time": datetime.datetime.now(),
        }
        defaults.update(params)
        return Journey.objects.create(**defaults)


def get_detail_url(journey_id: int):
    return reverse("train-station:journey-detail", args=[journey_id])


class AnonymousJourneyApiTests(APITestCase):
    """Here authenticated and anonymous users have the same level of access"""

    def test_list_retrieve_methods_allowed(self):
        sample_journey()
        res = self.client.get(JOURNEY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_returns_correct_data(self):
        route_two = sample_route(
            source=sample_station(name="third"),
            destination=sample_station(name="fourth"),
        )
        sample_journey()
        sample_journey(route=route_two)
        journeys = Journey.objects.all().annotate(
            tickets_available=(
                F("train__cargo_num") * F("train__places_in_cargo")
                - Count(F("tickets"))
            )
        )
        journey_one, journey_two = journeys[0], journeys[1]
        res = self.client.get(JOURNEY_URL)
        serializer = JourneyListSerializer(
            [journey_one, journey_two], many=True
        )
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_returns_correct_data(self):
        sample_journey()
        journey = Journey.objects.all().annotate(
            tickets_available=(
                F("train__cargo_num") * F("train__places_in_cargo")
                - Count(F("tickets"))
            )
        )[0]
        serializer = JourneyDetailSerializer(journey, many=False)
        res = self.client.get(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filtering_by_source_destination(self):
        first = sample_station(name="first")
        second = sample_station(name="second")
        third = sample_station(name="third")

        route_one = sample_route(source=first, destination=second)
        route_two = sample_route(source=third, destination_n="fourth")
        route_three = sample_route(source=third, destination=second)

        sample_journey(route=route_one)
        sample_journey(route=route_two)
        sample_journey(route=route_three)

        journeys = Journey.objects.all().annotate(
            tickets_available=(
                F("train__cargo_num") * F("train__places_in_cargo")
                - Count(F("tickets"))
            )
        )
        journey_one = JourneyListSerializer(journeys[0], many=False).data
        journey_two = JourneyListSerializer(journeys[1], many=False).data
        journey_three = JourneyListSerializer(journeys[2], many=False).data

        res = self.client.get(
            JOURNEY_URL,
            data={"source": "third"},
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(journey_two, res.data)
        self.assertIn(journey_three, res.data)
        self.assertNotIn(journey_one, res.data)

        res = self.client.get(
            JOURNEY_URL,
            data={"destination": "second"},
            content_type="application/json",
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(journey_two, res.data)
        self.assertIn(journey_three, res.data)
        self.assertIn(journey_one, res.data)

    def test_filtering_by_date_and_time(self):
        with override_settings(USE_TZ=False):
            datetime_one = datetime.datetime(
                year=2023,
                month=4,
                day=1,
                hour=12,
            )
            datetime_two = datetime.datetime(
                year=2023,
                month=4,
                day=1,
                hour=13,
            )
            datetime_three = datetime.datetime(
                year=2023,
                month=4,
                day=2,
                hour=12,
            )
            sample_journey(departure_time=datetime_one)
            sample_journey(departure_time=datetime_two)
            sample_journey(departure_time=datetime_three)

            journeys = Journey.objects.all().annotate(
                tickets_available=(
                    F("train__cargo_num") * F("train__places_in_cargo")
                    - Count(F("tickets"))
                )
            ).order_by("departure_time ")

            res = self.client.generic(
                "GET",
                JOURNEY_URL + "?departure_date=2023-04-01"
            )
            april_second = JourneyListSerializer(journeys[0], many=False)
            april_first_two = JourneyListSerializer(journeys[1], many=False)
            april_first_one = JourneyListSerializer(journeys[2], many=False)

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn(april_first_one.data, res.data)
            self.assertIn(april_first_two.data, res.data)
            self.assertNotIn(april_second.data, res.data)

            res = self.client.generic(
                "GET",
                JOURNEY_URL + "?departure_time=12:00"
            )

            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn(april_first_one.data, res.data)
            self.assertIn(april_second.data, res.data)
            self.assertNotIn(april_first_one.data, res.data)

    def test_create_method_forbidden(self):
        sample_train()
        sample_route()
        payload = json.dumps(
            {
                "train": 1,
                "route": 1,
                "departure_time": datetime.datetime.now(),
            },
            default=serialize_datetime,
        )
        res = self.client.post(
            JOURNEY_URL, data=payload, content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_method_forbidden(self):
        payload = json.dumps(
            {
                "train": 2,
                "route": 1,
                "departure_time": datetime.datetime.now(),
            },
            default=serialize_datetime,
        )
        sample_train()
        sample_journey()
        res = self.client.put(
            get_detail_url(1), data=payload, content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_forbidden(self):
        sample_journey()
        sample_crew()
        sample_crew()
        res = self.client.patch(
            get_detail_url(1),
            data=json.dumps({"crew_members": [1, 2]}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_method_forbidden(self):
        sample_journey()
        res = self.client.delete(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PublicJourneyApiTest(APITestCase):
    """Check that authenticated users don't have too much access"""
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(
            email="user@hmail.com", password="32r@!rgaf"
        )

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_create_method_forbidden(self):
        sample_train()
        sample_route()
        payload = json.dumps(
            {
                "train": 1,
                "route": 1,
                "departure_time": datetime.datetime.now(),
            },
            default=serialize_datetime,
        )
        res = self.client.post(
            JOURNEY_URL, data=payload, content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_method_forbidden(self):
        payload = json.dumps(
            {
                "train": 2,
                "route": 1,
                "departure_time": datetime.datetime.now(),
            },
            default=serialize_datetime,
        )
        sample_train()
        sample_journey()
        res = self.client.put(
            get_detail_url(1), data=payload, content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_forbidden(self):
        sample_journey()
        sample_crew()
        sample_crew()
        res = self.client.patch(
            get_detail_url(1),
            data=json.dumps({"crew_members": [1, 2]}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_method_forbidden(self):
        sample_journey()
        res = self.client.delete(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminJourneyApiTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="BAueai32!"
        )

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_create_allowed(self):
        sample_train()
        sample_route()
        sample_crew()
        payload = json.dumps(
            {
                "train": 1,
                "route": 1,
                "departure_time": datetime.datetime.now().isoformat(),
                "crew_members": [1],
            },
            default=serialize_datetime,
        )
        res = self.client.post(
            JOURNEY_URL, data=payload, content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_partial_update_allowed(self):
        sample_crew()
        payload = json.dumps(
            {
                "train": 2,
                "route": 1,
                "departure_time": datetime.datetime.now(),
                "crew_members": [1],
            },
            default=serialize_datetime,
        )
        sample_train()
        sample_journey()
        res = self.client.put(
            get_detail_url(1), data=payload, content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        sample_crew()
        res = self.client.patch(
            get_detail_url(1),
            data=json.dumps({"crew_members": [2]}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_allowed(self):
        sample_journey()
        res = self.client.delete(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
