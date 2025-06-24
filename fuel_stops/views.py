import logging
from decimal import Decimal

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from fuel_stops.serializers import OptimalFuelStopRouteSerializer
from fuel_stops.services.route_optimizer_service import RouteOptimizer
from fuel_stops.utils.open_route_service import OpenRouteServiceClient

logger = logging.getLogger(__name__)

MILES_TO_METERS = 1609.34


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

        route_data = OpenRouteServiceClient().get_route(
            (start_lon, start_lat), (end_lon, end_lat)
        )
        logger.error(f"Route data: {route_data}")
        if not route_data:
            return Response(
                {"error": "Failed to fetch route"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        optimizer = RouteOptimizer(
            start=(start_lon, start_lat),
            steps=route_data.get("steps", []),
            vehicle_range_miles=500,
            mpg=10,
        )

        try:
            fuel_stops, total_cost = optimizer.compute_optimal_stops()
        except Exception as e:
            logger.error(f"Error optimizing fuel stops: {e}")
            return Response({"error": "Route optimization failed"}, status=500)

        return Response(
            {
                "total_cost": total_cost.quantize(Decimal("0.00")),
                "fuel_stops": fuel_stops,
            }
        )
