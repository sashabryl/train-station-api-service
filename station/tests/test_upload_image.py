import os
import tempfile
import uuid

from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from station.models import Station, TrainType, Train


STATION_URL = reverse("train-station:station-list")
TRAIN_URL = reverse("train-station:train-list")


def sample_station(**params):
    defaults = {
        "name": f"Sample vokzal{uuid.uuid4()}",
        "latitude": 10.15,
        "longitude": 32.14,
    }
    defaults.update(params)

    return Station.objects.create(**defaults)


def sample_train_type(name: str = f"express{uuid.uuid4()}"):
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


class UnauthorizedImageUploadTests(APITestCase):
    def setUp(self) -> None:
        self.station = sample_station()
        self.train = sample_train()
        self.client.force_authenticate(self.user)

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user = get_user_model().objects.create(
            email="noright@gmail.com", password="e3AWF21!"
        )

    def test_upload_image_to_station(self):
        """Test uploading an image to station without any right to do so"""
        url = image_upload_url_station(self.station.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.station.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_image_to_train(self):
        """Test uploading an image to train without any right to do so"""
        url = image_upload_url_train(self.train.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.station.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class StationImageUploadTests(APITestCase):
    def setUp(self):
        self.station = sample_station()
        self.client.force_authenticate(self.user)

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user = get_user_model().objects.create_superuser(
            "my123@project.com", "password"
        )

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
        station = Station.objects.get(name="The vokzal")
        self.assertFalse(station.image)


class TrainImageUploadTests(APITestCase):
    def setUp(self):
        self.client.force_authenticate(self.user)
        self.train = sample_train()

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user = get_user_model().objects.create_superuser(
            "my123@project.com", "password"
        )

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
                    "train_type": 1,
                    "image": ntf,
                },
                format="multipart",
            )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Train.objects.filter(name="Le train grand").exists())
