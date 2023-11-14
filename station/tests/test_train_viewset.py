import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from station.models import TrainType, Train
from station.serializers import TrainListSerializer

TRAIN_URL = reverse("train-station:train-list")


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


def get_detail_url(train_id: int):
    return reverse("train-station:train-detail", args=[train_id])


class AnonymousTrainApiTests(TestCase):
    """Here authenticated and anonymous users have the same level of access"""

    def setUp(self):
        self.client = APIClient()

    def test_filtering_by_name(self):
        train_one = sample_train(name="train1")
        train_two = sample_train(name="train2")
        train_three = sample_train(name="bike")

        res = self.client.get(TRAIN_URL, data={"name": "train"})
        serializer = TrainListSerializer([train_one, train_two], many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class PublicTrainApiTests(TestCase):
    """Check for social equality rights observance"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="test@gnail.com", password="!@eawr@3"
        )
        self.client.force_authenticate(self.user)

    def test_create_method_forbidden(self):
        payload = {
            "name": "train",
            "cargo_num": 9,
            "places_in_cargo": 10,
            "train_type": sample_train_type(),
        }
        res = self.client.post(TRAIN_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_method_forbidden(self):
        payload = {
            "name": "train",
            "cargo_num": 9,
            "places_in_cargo": 10,
            "train_type": sample_train_type(),
        }
        sample_train()
        res = self.client.put(get_detail_url(1), data=payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_forbidden(self):
        sample_train()
        res = self.client.patch(get_detail_url(1), data={"name": "updated"})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_method_forbidden(self):
        sample_train()
        res = self.client.delete(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
