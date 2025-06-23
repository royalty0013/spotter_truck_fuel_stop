from django.contrib import admin

from fuel_ups.models import FuelStop


@admin.register(FuelStop)
class FuelStopAdmin(admin.ModelAdmin):
    list_display = (
        "opis_truckstop",
        "truckstop_name",
        "address",
        "city",
        "state",
        "rack_id",
        "retail_price",
        "point",
    )
