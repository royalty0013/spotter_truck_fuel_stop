import logging

import openrouteservice
from decouple import config

logger = logging.getLogger(__name__)


class OpenRouteServiceClient:
    def __init__(self):
        self.client = openrouteservice.Client(key=config("OPENROUTESERVICE_API_KEY"))

    def get_route(self, origin: tuple, destination: tuple) -> dict:
        """Fetches the route between two points using OpenRouteService.

        Args:
            origin (tuple): The starting point as a tuple of (longitude, latitude).
            destination (tuple): The destination point as a tuple of (longitude, latitude).

        Returns:
            dict: The route data in GeoJSON format.
        """
        try:
            response = self.client.directions(
                coordinates=[origin, destination],
                profile="driving-hgv",
                format="geojson",
            )
            summary = response["features"][0]["properties"]["summary"]
            steps = response["features"][0]["properties"]["segments"][0]["steps"]

            simplified = {
                "total_distance": summary["distance"],  # meters
                "total_duration": summary["duration"],  # seconds
                "steps": [
                    {
                        "distance": step["distance"],
                        "duration": step["duration"],
                        "instruction": step.get("instruction", ""),
                        "location": step.get("location", []),
                    }
                    for step in steps
                ],
                "geometry": response["features"][0][
                    "geometry"
                ],  # LineString for mapping (optional)
            }

            return simplified
        except Exception as e:
            logger.error(f"Error fetching route: {e}")
            return None
