import logging
from decimal import Decimal

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from fuel_stops.constants import MPG, VEHICLE_RANGE_MILES
from fuel_stops.serializers import OptimalFuelStopRouteSerializer
from fuel_stops.services.route_optimizer_service import RouteOptimizerService
from fuel_stops.utils.open_route_service import OpenRouteServiceClient

logger = logging.getLogger(__name__)


class OptimalFuelStopRouteAPIView(APIView):
    def post(self, request):
        serializer = OptimalFuelStopRouteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        start_lon = validated_data["start_lon"]
        start_lat = validated_data["start_lat"]
        end_lon = validated_data["end_lon"]
        end_lat = validated_data["end_lat"]

        try:
            ors_client = OpenRouteServiceClient()
            route_data = ors_client.get_route(
                (start_lon, start_lat), (end_lon, end_lat)
            )

            optimizer = RouteOptimizerService(
                start=(start_lon, start_lat),
                steps=route_data.get("steps", []),
                vehicle_range_miles=VEHICLE_RANGE_MILES,
                mpg=MPG,
            )
            fuel_stops, total_cost = optimizer.compute_optimal_stops()

            map_data = optimizer.generate_map_geojson(
                route_data.get("geometry"), fuel_stops
            )
        except ValidationError as e:
            logger.error(f"Error optimizing fuel stops: {e}")
            return Response(
                {"error": "Route optimization failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "total_cost": total_cost.quantize(Decimal("0.00")),
                "fuel_stops": fuel_stops,
                "map_data": map_data,
            },
            status=status.HTTP_200_OK,
        )
