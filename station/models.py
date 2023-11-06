from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField()
    places_in_cargo = models.IntegerField()
    train_type = models.ForeignKey(
        "TrainType", on_delete=models.CASCADE, related_name="trains"
    )

    class Meta:
        ordering = ["name"]

    @property
    def capacity(self) -> int:
        return self.cargo_num * self.places_in_cargo

    def __str__(self):
        return f"{self.name} ({self.train_type}, {self.capacity} places)"


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField()
    longtitude = models.FloatField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longtitude})"


class Route(models.Model):
    source = models.ForeignKey(
        "Station", on_delete=models.CASCADE, related_name="routes_from"
    )
    destination = models.ForeignKey(
        "Station", on_delete=models.CASCADE, related_name="routes_to"
    )
    distance = models.IntegerField()

    class Meta:
        ordering = ["-distance"]

    def __str__(self):
        return f"{self.source.name} - {self.destination.name}"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Journey(models.Model):
    route = models.ForeignKey(
        "Route", on_delete=models.CASCADE, related_name="journeys"
    )
    train = models.ForeignKey(
        "Train", on_delete=models.CASCADE, related_name="journeys"
    )
    departure_time = models.DateTimeField()
    crew_members = models.ManyToManyField("Crew", related_name="journeys")

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self):
        return f"{self.route}, {self.departure_time}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(
        "Journey", on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["seat", "cargo", "journey"],
                name="unique_seat_booking",
            )
        ]

    @staticmethod
    def validata_seat(
        seat: int,
        max_seats: int,
        cargo: int,
        max_cargos: int,
        exception_to_raise: Exception,
    ):
        if not 1 <= seat <= max_seats:
            raise exception_to_raise(
                f"Number of seat should be in range "
                f"from 1 to {max_seats}, not {seat}"
            )
        if not 1 <= cargo <= max_cargos:
            raise exception_to_raise(
                f"Number of cargo should be in range "
                f"from 1 to {max_cargos}, not {cargo}"
            )

    def clean(self):
        Ticket.validata_seat(
            self.seat,
            self.journey.train.places_in_cargo,
            self.cargo,
            self.journey.train.cargo_num,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None
    ):
        self.full_clean()
        return super().save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return (
            f"{self.journey.route}-"
            f", departure: {self.journey.departure_time}"
        )
