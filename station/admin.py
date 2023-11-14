from django.contrib.admin import ModelAdmin, TabularInline

from station.models import (
    TrainType,
    Train,
    Order,
    Ticket,
    Crew,
    Station,
    Route,
    Journey,
)


from django.contrib import admin


admin.site.register(TrainType)


@admin.register(Train)
class TrainAdmin(ModelAdmin):
    list_display = (
        "name",
        "cargo_num",
        "places_in_cargo",
        "train_type",
    )
    list_filter = ("train_type",)


@admin.register(Crew)
class CrewAdmin(ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
    )


@admin.register(Station)
class StationAdmin(ModelAdmin):
    list_display = (
        "name",
        "latitude",
        "longitude",
    )


@admin.register(Route)
class RouteAdmin(ModelAdmin):
    list_display = (
        "source",
        "destination",
        "distance",
    )
    list_filter = (
        "source",
        "destination",
    )
    search_fields = ("__str__",)


@admin.register(Journey)
class JourneyAdmin(ModelAdmin):
    list_display = (
        "train",
        "route",
        "departure_time",
    )
    list_filter = (
        "train",
        "route",
    )


class TicketInline(TabularInline):
    model = Ticket


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    inlines = [TicketInline]

    list_display = (
        "created_at",
        "user",
    )
    search_fields = ("user",)
