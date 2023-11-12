import datetime
import random
import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from station.models import Station, Journey, Ticket, Order, Route, Crew, Train, TrainType


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


class StationModelTest(TestCase):
    def test_longitude_latitude_validation(self):
        with self.assertRaises(ValidationError):
            Station.objects.create(
                name="station", longitude=361, latitude=32.4
            )


class TicketModelTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create(
            email="user@hmai.com", password="deaf#@314"
        )
        self.order = create_order(self.user)

    def test_unique_set_journey_validation(self):
        same_journey = sample_journey()
        create_ticket(order=self.order, journey=same_journey)
        with self.assertRaises(ValidationError):
            create_ticket(order=self.order, journey=same_journey)

    def test_validate_seat_and_cargo_in_available_range(self):
        with self.assertRaises(ValidationError):
            create_ticket(order=self.order, cargo=11)

        with self.assertRaises(ValidationError):
            create_ticket(order=self.order, seat=16)
