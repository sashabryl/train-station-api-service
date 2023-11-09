from django.db.models import Q, F, Count
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from station.models import (
    TrainType,
    Train,
    Station,
    Route,
    Crew,
    Journey,
    Order,
)
from station.serializers import (
    TrainTypeSerializer,
    TrainSerializer,
    TrainListSerializer,
    StationSerializer,
    RouteSerializer,
    RouteDetailSerializer,
    RouteListSerializer,
    CrewSerializer,
    JourneySerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
)


class TrainTypeViewSet(viewsets.ModelViewSet):
    serializer_class = TrainTypeSerializer
    queryset = TrainType.objects.all()


class TrainViewSet(viewsets.ModelViewSet):
    serializer_class = TrainSerializer
    queryset = Train.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        if self.action == "list":
            queryset = queryset.select_related("train_type")

        return queryset


class StationViewSet(viewsets.ModelViewSet):
    serializer_class = StationSerializer
    queryset = Station.objects.all()

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset

    def get_serializer_class(self):
        return self.serializer_class


class RouteViewSet(viewsets.ModelViewSet):
    serializer_class = RouteSerializer
    queryset = Route.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        source = self.request.query_params.get("source")
        if source:
            queryset = queryset.filter(source__name__icontains=source)

        destination = self.request.query_params.get("destination")
        if destination:
            queryset = queryset.filter(
                destination__name__icontains=destination
            )

        if self.action == "list":
            queryset = queryset.select_related("source", "destination")

        return queryset


class CrewViewSet(viewsets.ModelViewSet):
    serializer_class = CrewSerializer
    queryset = Crew.objects.all()

    def get_queryset(self):
        queryset = self.queryset

        full_name = self.request.query_params.get("full_name")
        if full_name:
            full_name = full_name.split(" ") + [None]
            first_name, last_name = full_name[0], full_name[1]

            search_for_first_name = queryset.filter(
                Q(first_name__icontains=first_name)
                | Q(last_name__icontains=first_name)
            )

            if last_name:
                search_for_last_name = queryset.filter(
                    Q(first_name__icontains=last_name)
                    | Q(last_name__icontains=last_name)
                )
                queryset = search_for_first_name | search_for_last_name
            else:
                queryset = search_for_first_name

        return queryset


class JourneyViewSet(viewsets.ModelViewSet):
    serializer_class = JourneySerializer
    queryset = Journey.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        departure_date = self.request.query_params.get("departure_date")
        departure_time = self.request.query_params.get("departure_time")

        if source:
            queryset = queryset.filter(route__source__name__icontains=source)

        if destination:
            queryset = queryset.filter(route__destination__name__icontains=source)

        if departure_date:
            queryset = queryset.filter(departure_time__date=departure_date)

        if departure_time:
            queryset = queryset.filter(departure_time__time=departure_time)

        if self.action == "list":
            queryset = (
                queryset
                .select_related(
                    "train__train_type",
                    "route__source",
                    "route__destination"
                )
                .prefetch_related("crew_members")
                .annotate(
                    tickets_available=(
                        (
                            F("train__cargo_num") *
                            F("train__places_in_cargo") -
                            Count("tickets")
                        )
                    )
                )
            )
        return queryset


class OrderPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = "page_size"
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.prefetch_related(
        "tickets__journey__route__source",
        "tickets__journey__route__destination",
    )
    pagination_class = OrderPagination

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related(
                "tickets__journey__route__source",
                "tickets__journey__route__destination",
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
