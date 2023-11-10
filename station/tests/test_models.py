import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from station.models import Train, TrainType, Station, Route, Journey, Ticket, Order


def sample_station(**params):
    defaults = {
        "name": "Sample vokzal",
        "latitude": 10.15,
        "longitude": 32.14,
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


def sample_train_type(name: str = "express"):
    return TrainType.objects.create(name=name)


def sample_train(**params):
    defaults = {
        "name": "Lincorn",
        "cargo_num": 10,
        "places_in_cargo": 15,
        "train_type": sample_train_type(),
    }
    defaults.update(params)

    return Train.objects.create(**defaults)


def sample_route(**params):
    defaults = {
        "source": sample_station(name="source"),
        "destination": sample_station(name="destination"),
        "distance": 100
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


class TestTrainModel(TestCase):
    def test_capacity_property(self):
        train = sample_train()
        self.assertEqual(train.capacity, 150)

    def test_str(self):
        train = sample_train()
        self.assertEqual(
            train.__str__(),
            f"{train.name} ({train.train_type.name}, {train.capacity} places)"
        )


class TestStationModel(TestCase):
    def test_validation_on_longitude_latitude(self):
        pass

    def test_str(self):
        station = sample_station()
        self.assertEqual(
            station.__str__(),
            f"{station.name} ({station.latitude}, {station.longitude})"
        )


class TestTicketModel(TestCase):
    def test_validation(self):
        journey = Journey.objects.create(
            train=sample_train(),
            route=sample_route(),
            departure_time=datetime.datetime.now()
        )
        user = get_user_model().objects.create_user(
            email="user@gmail.com", password="fjeiwoa!"
        )
        order = Order.objects.create(user=user)
        Ticket.objects.create(
            order=order,
            journey=journey,
            cargo=1,
            seat=1
        )

        with self.assertRaises(ValidationError):
            already_booked_ticket = Ticket.objects.create(
                order=order,
                journey=journey,
                cargo=1,
                seat=1
            )

        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                order=order,
                journey=journey,
                cargo=100,
                seat=1
            )

        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                order=order,
                journey=journey,
                cargo=1,
                seat=111
            )
