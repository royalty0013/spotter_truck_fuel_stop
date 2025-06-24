from rest_framework import serializers


class OptimalFuelStopRouteSerializer(serializers.Serializer):
    start_lat = serializers.FloatField()
    start_lon = serializers.FloatField()
    end_lat = serializers.FloatField()
    end_lon = serializers.FloatField()

    def validate(self, data):
        # Validate latitudes
        for lat_field in ["start_lat", "end_lat"]:
            if not (-90 <= data[lat_field] <= 90):
                raise serializers.ValidationError(
                    {"error": f"{lat_field} must be between -90 and 90."}
                )

        # Validate longitudes
        for lon_field in ["start_lon", "end_lon"]:
            if not (-180 <= data[lon_field] <= 180):
                raise serializers.ValidationError(
                    {"error": f"{lon_field} must be between -180 and 180."}
                )

        return data
