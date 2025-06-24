from decimal import ROUND_HALF_UP, Decimal

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from geojson import Feature, FeatureCollection
from geojson import Point as P
from rest_framework.exceptions import ValidationError

from fuel_stops.models import FuelStop

MILES_TO_METERS = 1609.34


class RouteOptimizerService:
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
        """Finds the nearest fuel stop to the given point.

        Args:
            point (tuple): The point to find the nearest fuel stop to.
            within (float): The maximum distance to search for a fuel stop.

        Returns:
            FuelStop: The nearest fuel stop to the given point.
        """
        lon, lat = point
        geo_point = Point(lon, lat)
        return (
            FuelStop.objects.filter(point__dwithin=(geo_point, D(m=within)))
            .order_by("retail_price")
            .first()
        )

    def compute_optimal_stops(self):
        """Computes the optimal fuel stops for the given route.

        Raises:
            Exception: If no fuel stop is found within range.

        Returns:
            tuple: A tuple containing the list of fuel stops and the total cost.
        """
        for step in self.steps:
            distance_to_next = step["distance"]
            if self.remaining_range < distance_to_next:
                nearest_stop = self.find_nearest_fuel_stop(
                    self.current_pos, within=100 * MILES_TO_METERS
                )
                if not nearest_stop:
                    raise ValidationError("No fuel stop found within range.")

                gallons_bought = Decimal(self.remaining_range / self.mpg).quantize(
                    Decimal("0.000"), rounding=ROUND_HALF_UP
                )
                cost = gallons_bought * nearest_stop.retail_price
                self.total_cost += cost

                self.fuel_stops.append(
                    {
                        "truckstop_name": nearest_stop.truckstop_name,
                        "retail_price": nearest_stop.retail_price,
                        "latitude": nearest_stop.point.y,
                        "longitude": nearest_stop.point.x,
                        "gallons_bought": gallons_bought,
                    }
                )

                self.remaining_range = self.vehicle_range_meters
                self.current_pos = (nearest_stop.point.x, nearest_stop.point.y)

            self.remaining_range -= distance_to_next

        return self.fuel_stops, self.total_cost

    def generate_map_geojson(self, route_geometry, fuel_stops):
        """Generates a GeoJSON object for the map data.

        Args:
            route_geometry (LineString): The route geometry.
            fuel_stops (list): List of fuel stops.

        Returns:
            FeatureCollection: The GeoJSON object for the map data.
        """

        features = []

        features.append(Feature(geometry=route_geometry))

        for stop in fuel_stops:
            features.append(
                Feature(
                    geometry=P((stop["longitude"], stop["latitude"])),
                    properties={
                        "truckstop_name": stop["truckstop_name"],
                        "retail_price": stop["retail_price"],
                        "gallons_bought": stop["gallons_bought"],
                    },
                )
            )

        return FeatureCollection(features)
