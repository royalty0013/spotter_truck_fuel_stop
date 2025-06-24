from decimal import ROUND_HALF_UP, Decimal

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from fuel_stops.models import FuelStop

MILES_TO_METERS = 1609.34


class RouteOptimizer:
    def __init__(
        self, start: tuple, steps: list, vehicle_range_miles: float, mpg: float
    ):
        self.start = start
        self.steps = steps
        self.vehicle_range_meters = vehicle_range_miles * MILES_TO_METERS
        self.mpg = mpg
        self.remaining_range = self.vehicle_range_meters
        self.current_pos = start
        self.fuel_stops = []
        self.total_cost = Decimal("0.00")

    def find_nearest_fuel_stop(self, point: tuple, within: float) -> FuelStop:
        lon, lat = point
        geo_point = Point(lon, lat)
        return (
            FuelStop.objects.filter(point__dwithin=(geo_point, D(m=within)))
            .order_by("retail_price")
            .first()
        )

    def compute_optimal_stops(self):
        for step in self.steps:
            distance_to_next = step["distance"]
            if self.remaining_range < distance_to_next:
                nearest_stop = self.find_nearest_fuel_stop(
                    self.current_pos, within=100 * MILES_TO_METERS
                )
                if not nearest_stop:
                    raise Exception("No fuel stop found within range.")

                gallons = Decimal(self.remaining_range / self.mpg).quantize(
                    Decimal("0.000"), rounding=ROUND_HALF_UP
                )
                cost = gallons * nearest_stop.retail_price
                self.total_cost += cost

                self.fuel_stops.append(
                    {
                        "truckstop_name": nearest_stop.truckstop_name,
                        "retail_price": nearest_stop.retail_price,
                        "latitude": nearest_stop.point.y,
                        "longitude": nearest_stop.point.x,
                        "gallons_bought": gallons,
                    }
                )

                self.remaining_range = self.vehicle_range_meters
                self.current_pos = (nearest_stop.point.x, nearest_stop.point.y)

            self.remaining_range -= distance_to_next

        return self.fuel_stops, self.total_cost
