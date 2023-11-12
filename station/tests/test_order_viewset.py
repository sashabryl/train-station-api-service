import datetime
import json
import random
import time
import uuid

from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from rest_framework import status

from station.models import Train, Station, Route, Crew, TrainType, Journey, Order, Ticket
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from station.serializers import OrderListSerializer

ORDER_URL = reverse("train-station:order-list")


def get_detail_url(order_id: int):
    return reverse("train-station:order-detail", args=[order_id])


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


def create_ticket(order, **params):
    defaults = {
        "seat": 1,
        "cargo": 1,
        "journey": sample_journey(),
        "order": order,
    }
    defaults.update(params)
    return Ticket.objects.create(**defaults)


def create_order(user):
    return Order.objects.create(user=user)


class AnonymousOrderApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="user@hmail.com", password="efeai341@"
        )
        order = create_order(self.user)
        create_ticket(order)

    def test_list_forbidden(self):
        res = self.client.get(ORDER_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PublicOrderApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="user@gmali.com", password="dea@#31f"
        )
        self.client.force_authenticate(self.user)

    def test_detail_page_not_exists(self):
        order = create_order(self.user)
        create_ticket(order)
        with self.assertRaises(NoReverseMatch):
            get_detail_url(1)

    def test_list_returns_correct_data(self):
        order_one = create_order(self.user)
        create_ticket(order_one)
        time.sleep(0.5)
        order_two = create_order(self.user)
        create_ticket(order_two, seat=2)
        my_orders = OrderListSerializer([order_one, order_two], many=True)

        another_user = get_user_model().objects.create(
            email="someone@gmoal.com", password="dewaf@#132"
        )
        order_three = create_order(another_user)
        create_ticket(order_three, seat=3)

        res = self.client.get(ORDER_URL)
        results = json.loads(json.dumps(res.data)).get("results")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(results[0], my_orders.data[1])
        self.assertEqual(results[1], my_orders.data[0])

    def test_create_method_works(self):
        sample_journey()
        payload = {
            "tickets": [
                {"seat": 1, "cargo": 1, "journey": 1},
            ],
        }
        res = self.client.post(ORDER_URL, data=payload)
        print(res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(user=self.user).exists())


