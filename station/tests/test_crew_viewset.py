import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from station.models import Crew
from station.serializers import CrewSerializer, CrewDetailSerializer

CREW_URL = reverse("train-station:crew-list")


def sample_crew(**params):
    defaults = {"first_name": "sasha", "last_name": "bryl"}
    defaults.update(params)

    return Crew.objects.create(**defaults)


def get_detail_url(station_id: int):
    return reverse("train-station:crew-detail", args=[station_id])


class AnonymousCrewApiTest(APITestCase):

    def test_list_method_forbidden(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_method_forbidden(self):
        payload = {"first_name": "bob", "last_name": "alice"}
        res = self.client.post(CREW_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_method_forbidden(self):
        payload = {"first_name": "bob", "last_name": "alice"}
        sample_crew()
        res = self.client.put(get_detail_url(1), data=payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_forbidden(self):
        sample_crew()
        res = self.client.patch(
            get_detail_url(1), data={"first_name": "updated"}
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_method_forbidden(self):
        sample_crew()
        res = self.client.delete(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PublicCrewApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create(
            email="test@gnail.com", password="!@eawr@3"
        )

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_list_method_forbidden(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_method_forbidden(self):
        payload = json.dumps({"first_name": "bob", "last_name": "alice"})
        res = self.client.post(
            CREW_URL, data=payload, content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_method_forbidden(self):
        payload = {"first_name": "bob", "last_name": "alice"}
        sample_crew()
        res = self.client.put(
            get_detail_url(1),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_forbidden(self):
        sample_crew()
        res = self.client.patch(
            get_detail_url(1),
            data=json.dumps({"first_name": "updated"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_method_forbidden(self):
        sample_crew()
        res = self.client.delete(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            email="admin@admin.com", password="BAueai32!"
        )

    def setUp(self) -> None:
        self.client.force_authenticate(self.user)

    def test_list_returns_correct_data(self):
        bob = sample_crew()
        alas = sample_crew()
        res = self.client.get(CREW_URL)
        serializer = CrewSerializer([bob, alas], many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_retrieve_methods_allowed(self):
        sample_crew()
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_returns_correct_data(self):
        crew = sample_crew()
        serializer = CrewDetailSerializer(crew, many=False)
        res = self.client.get(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filtering_by_full_name(self):
        bob = sample_crew(first_name="Bob", last_name="Robertson")
        alan = sample_crew(first_name="Alan", last_name="Douglas")
        alice = sample_crew(first_name="Alice", last_name="Robertson")

        res = self.client.generic(
            "GET",
            CREW_URL + "?full_name=rob",
        )
        alice = CrewSerializer(alice, many=False)
        bob = CrewSerializer(bob, many=False)
        alan = CrewSerializer(alan, many=False)

        self.assertIn(alice.data, res.data)
        self.assertIn(bob.data, res.data)
        self.assertNotIn(alan.data, res.data)

        res = self.client.generic(
            "GET",
            CREW_URL + "?full_name=Alan Douglas"
        )

        self.assertNotIn(alice.data, res.data)
        self.assertNotIn(bob.data, res.data)
        self.assertIn(alan.data, res.data)

    def test_create_allowed(self):
        payload = json.dumps(
            {
                "email": "bob@gmail.com",
                "first_name": "bob",
                "last_name": "alice",
            }
        )
        res = self.client.post(
            CREW_URL, data=payload, content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_partial_update_allowed(self):
        sample_crew()
        payload = json.dumps(
            {
                "email": "bob@gmail.com",
                "first_name": "robert",
                "last_name": "alice",
            }
        )
        res = self.client.put(
            get_detail_url(1), data=payload, content_type="application/json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.patch(
            get_detail_url(1),
            data=json.dumps({"last_name": "new"}),
            content_type="application/json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_allowed(self):
        sample_crew()
        res = self.client.delete(get_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
