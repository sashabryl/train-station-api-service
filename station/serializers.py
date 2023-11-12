from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from station.models import (
    TrainType,
    Train,
    Station,
    Route,
    Crew,
    Journey,
    Ticket,
    Order,
)


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = (
            "id",
            "name",
        )


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "capacity",
        )


class TrainImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "image")


class TrainListSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )

    class Meta(TrainSerializer.Meta):
        fields = TrainSerializer.Meta.fields + ("image",)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")

    def create(self, validated_data):
        station = Station(
            name=validated_data.get("name"),
            latitude=validated_data.get("latitude"),
            longitude=validated_data.get("longitude")
        )
        station.save()
        return station


class StationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "image")


class StationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude", "image")


class StationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "image")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance", "description")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )


class RouteDetailSerializer(RouteSerializer):
    source = StationListSerializer(many=False, read_only=True)
    destination = StationListSerializer(many=False, read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "email")
        extra_kwargs = {"email": {"write_only": True}}


class CrewDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "email")


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "crew_members",
        )


class JourneyListSerializer(JourneySerializer):
    route = serializers.StringRelatedField(many=False)
    tickets_available = serializers.IntegerField()
    train = serializers.StringRelatedField(many=False)
    crew_members = serializers.StringRelatedField(many=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "tickets_available",
            "train",
            "departure_time",
            "crew_members",
        )


class TicketCargoSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("cargo", "seat")


class JourneyDetailSerializer(JourneySerializer):
    route = RouteDetailSerializer(many=False)
    train = TrainListSerializer(many=False)
    crew_members = serializers.StringRelatedField(many=True)
    tickets_available = serializers.IntegerField()
    taken_seats = TicketCargoSeatSerializer(
        many=True, read_only=True, source="tickets"
    )

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "crew_members",
            "tickets_available",
            "taken_seats",
        )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")
        validators = [
            UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=["seat", "cargo", "journey"],
                message="This seat is already booked.",
            )
        ]

    def validate(self, attrs):
        data = super().validate(attrs)
        Ticket.validate_seat(
            attrs["seat"], attrs["cargo"], data["journey"], ValidationError
        )
        return data


class TicketListSerializer(TicketSerializer):
    journey = serializers.StringRelatedField(many=False)


class TicketSeatSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("seat", "cargo")


class TicketDetailSerializer(TicketSerializer):
    journey = JourneyListSerializer(read_only=True, many=False)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket in tickets:
                order.tickets.add(
                    Ticket.objects.create(order=order, **ticket)
                )
            order.save()
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(read_only=True, many=True)
