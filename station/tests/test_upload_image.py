import os
import tempfile

from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from station.models import Station, TrainType, Train


STATION_URL = reverse("train-station:station-list")
TRAIN_URL = reverse("train-station:train-list")


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


def image_upload_url_station(station_id):
    """Return URL for recipe image upload"""
    return reverse("train-station:station-upload-image", args=[station_id])


def detail_url_station(station_id):
    return reverse("train-station:station-detail", args=[station_id])


def image_upload_url_train(train_id):
    """Return URL for recipe image upload"""
    return reverse("train-station:train-upload-image", args=[train_id])


def detail_url_train(train_id):
    return reverse("train-station:train-detail", args=[train_id])


class StationImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "my123@project.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.station = sample_station()

    def tearDown(self):
        self.station.image.delete()

    def test_upload_image_to_station(self):
        """Test uploading an image to station"""
        url = image_upload_url_station(self.station.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.station.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.station.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url_station(self.station.id)
        res = self.client.post(
            url, {"image": "not image"}, format="multipart"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_station_list(self):
        url = STATION_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "The vokzal",
                    "longitude": 90.3,
                    "latitude": 32.4,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        station = Station.objects.get(name="The vokzal")
        self.assertFalse(station.image)


class TrainImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "my123@project.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.train = sample_train()
        self.train_type = sample_train_type("artillery")

    def tearDown(self):
        self.train.image.delete()

    def test_upload_image_to_train(self):
        """Test uploading an image to train"""
        url = image_upload_url_train(self.train.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.train.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.train.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url_train(self.train.id)
        res = self.client.post(
            url, {"image": "not image"}, format="multipart"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_train_list(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                TRAIN_URL,
                {
                    "name": "Le train grand",
                    "cargo_num": 2,
                    "places_in_cargo": 15,
                    "train_type": 2,
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        train = Train.objects.get(name="Le train grand")
        self.assertFalse(train.image)
