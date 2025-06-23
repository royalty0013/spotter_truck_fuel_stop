import logging
from decimal import ROUND_HALF_UP, Decimal

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework.response import Response
from rest_framework.views import APIView

from fuel_stops.models import FuelStop
from fuel_stops.utils.open_route_service import OpenRouteServiceClient

logger = logging.getLogger(__name__)

MILES_TO_METERS = 1609.34


class OptimalFuelStopRouteAPIView(APIView):
    def post(self, request):
        start_lat = float(request.data.get("start_lat"))
        start_lon = float(request.data.get("start_lon"))
        end_lat = float(request.data.get("end_lat"))
        end_lon = float(request.data.get("end_lon"))

        route_data = OpenRouteServiceClient().get_route(
            (start_lon, start_lat), (end_lon, end_lat)
        )
        logger.info(route_data)
        logger.info("*" * 30)

        if not route_data:
            return Response({"error": "Failed to fetch route"}, status=500)

        # total_distance_meters = route_data["total_distance"]
        steps = route_data["steps"]

        vehicle_range_meters = 500 * MILES_TO_METERS
        mpg = 10

        current_pos = (start_lon, start_lat)
        remaining_range = vehicle_range_meters
        fuel_stops = []
        total_cost = Decimal("0.00")

        for step in steps:
            distance_to_next = step["distance"]  # meters

            if remaining_range < distance_to_next:
                # Need to refuel before moving forward
                nearest_stop = self._find_nearest_fuel_stop(
                    current_pos, within=100 * MILES_TO_METERS
                )
                if not nearest_stop:
                    return Response({"error": "No fuel stop found nearby."}, status=400)

                fuel_needed = Decimal(remaining_range / mpg).quantize(
                    Decimal("0.000"), rounding=ROUND_HALF_UP
                )  # gallons
                total_cost += fuel_needed * nearest_stop.retail_price

                fuel_stops.append(
                    {
                        "truckstop_name": nearest_stop.truckstop_name,
                        "retail_price": nearest_stop.retail_price,
                        "latitude": nearest_stop.point.y,
                        "longitude": nearest_stop.point.x,
                        "gallons_bought": fuel_needed,
                    }
                )

                remaining_range = vehicle_range_meters
                current_pos = (nearest_stop.point.x, nearest_stop.point.y)

            remaining_range -= distance_to_next

        return Response(
            {
                "total_cost": total_cost.quantize(
                    Decimal("0.00"), rounding=ROUND_HALF_UP
                ),
                "fuel_stops": fuel_stops,
            }
        )

    def _find_nearest_fuel_stop(self, point, within):
        lon, lat = point
        pnt = Point(lon, lat)
        stops = FuelStop.objects.filter(point__dwithin=(pnt, D(m=within)))
        return stops.order_by("retail_price").first()
