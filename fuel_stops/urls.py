from django.urls import path

from fuel_stops.views import OptimalFuelStopRouteAPIView

urlpatterns = [
    path("fuel-stops/", OptimalFuelStopRouteAPIView.as_view(), name="fuel_stops"),
]
