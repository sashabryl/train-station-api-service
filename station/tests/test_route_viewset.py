# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APIClient
#
# from station.models import Station, Route
# from station.serializers import RouteListSerializer, RouteDetailSerializer
#
#
# ROUTE_URL = reverse("train_station:route-list")
#
#
# def sample_station(**params):
#     defaults = {
#         "name": "Sample vokzal",
#         "latitude": 10.15,
#         "longitude": 32.14,
#     }
#     defaults.update(params)
#
#     return Station.objects.create(**defaults)
#
#
# def sample_route(**params):
#     defaults = {
#         "source": sample_station(name="first"),
#         "destination": sample_station(name="second"),
#         "distance": 100,
#     }
#     defaults.update(params)
#     return Route.objects.create(**defaults)
#
#
# def get_detail_url(route_id: int):
#     return reverse("train_station:route-detail", args=[route_id])
#
#
# class PublicRouteApiTests(TestCase):
#     """Here authenticated and anonymous users have the same level of access"""
#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create(
#             email="test@gnail.com", password="!@eawr@3"
#         )
#         self.client.force_authenticate(self.user)
#
#     def test_list_retrieve_methods_allowed(self):
#         sample_route()
#         res = self.client.get(ROUTE_URL)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#
#         res = self.client.get(get_detail_url(1))
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#
#     def test_list_returns_correct_data(self):
#         route_one = sample_route()
#         route_two = sample_route(
#             source=sample_station(name="third"),
#             destination=sample_station(name="fourth")
#         )
#         res = self.client.get(ROUTE_URL)
#         serializer = RouteListSerializer([route_one, route_two], many=True)
#         self.assertEqual(res.data, serializer.data)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#
#     def test_retrieve_returns_correct_data(self):
#         route = sample_route()
#         serializer = RouteDetailSerializer(route, many=False)
#         res = self.client.get(get_detail_url(1))
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, serializer.data)
#
#     def test_filtering(self):
#         station_one = sample_station(name="st1")
#         station_two = sample_station(name="st2")
#         station_three = sample_station(name="st3")
#         route_one = sample_route()
#         route_two = sample_route(
#             source=station_one,
#             destination=station_two
#         )
#         route_three = sample_route(
#             source=station_one,
#             destination=station_three
#         )
#
#         res = self.client.get(ROUTE_URL, data={"source": "st1"})
#         from_st1 = RouteListSerializer(
#             [route_two, route_three], many=True
#         )
#
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, from_st1.data)
#
#         res = self.client.get(ROUTE_URL, data={"destination": "second"})
#         to_default_station = RouteListSerializer(route_one, many=True)
#
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, to_default_station.data)
#
#     def test_create_method_forbidden(self):
#         payload = {
#             "source": sample_station(name="first"),
#             "destination": sample_station(name="second"),
#             "distance": 100,
#         }
#         res = self.client.post(ROUTE_URL, data=payload)
#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#
#     def test_update_method_forbidden(self):
#         payload = {
#             "source": sample_station(name="third"),
#             "destination": sample_station(name="fourth"),
#             "distance": 200,
#         }
#         sample_route()
#         res = self.client.put(get_detail_url(1), data=payload)
#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#
#     def test_partial_update_forbidden(self):
#         sample_route()
#         res = self.client.patch(get_detail_url(1), data={"distance": 300})
#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#
#     def test_delete_method_forbidden(self):
#         sample_route()
#         res = self.client.delete(get_detail_url(1))
#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#
#
# class AdminStationApiTest(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_superuser(
#             email="admin@admin.com", password="BAueai32!"
#         )
#         self.client.force_authenticate(self.user)
#
#     def test_create_allowed(self):
#         payload = {
#             "source": sample_station(name="first"),
#             "destination": sample_station(name="second"),
#             "distance": 100,
#         }
#         res = self.client.post(ROUTE_URL, data=payload)
#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#
#     def test_update_partial_update_allowed(self):
#         sample_route()
#         payload = {
#             "source": sample_station(name="third"),
#             "destination": sample_station(name="fourth"),
#             "distance": 100,
#         }
#         res = self.client.put(get_detail_url(1), data=payload)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#
#         res = self.client.patch(get_detail_url(1), data={"distance": 200})
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#
#     def test_delete_allowed(self):
#         sample_route()
#         res = self.client.delete(get_detail_url(1))
#         self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)