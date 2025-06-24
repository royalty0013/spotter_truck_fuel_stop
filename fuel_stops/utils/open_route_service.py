import logging

import openrouteservice
from decouple import config
from django.core.cache import cache

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
            cache_key = f"ors_route_{origin[0]:.6f}_{origin[1]:.6f}_to_{destination[0]:.6f}_{destination[1]:.6f}"
            cached_response = cache.get(cache_key)

            if cached_response is not None:
                return cached_response

            full_geojson = self._fetch_full_route_from_ors(origin, destination)
            if not full_geojson:
                return None

            simplified = self._simplify_geojson(full_geojson)

            cache.set(cache_key, simplified, timeout=60 * 60 * 24)

            return simplified

        except Exception as e:
            logger.error(f"Error fetching route: {e}", exc_info=True)
            return None

    def _fetch_full_route_from_ors(self, origin: tuple, destination: tuple) -> dict:
        """Fetch raw GeoJSON response from OpenRouteService."""
        try:
            response = self.client.directions(
                coordinates=[origin, destination],
                profile="driving-hgv",
                format="geojson",
            )
            return response
        except Exception as e:
            logger.error(f"OpenRouteService request failed: {e}")
            return None

    def _simplify_geojson(self, geojson: dict) -> dict:
        """Convert full GeoJSON into simplified route info."""
        try:
            summary = geojson["features"][0]["properties"]["summary"]
            steps = geojson["features"][0]["properties"]["segments"][0]["steps"]

            return {
                "total_distance": summary["distance"],
                "total_duration": summary["duration"],
                "steps": [
                    {
                        "distance": step["distance"],
                        "duration": step["duration"],
                        "instruction": step.get("instruction", ""),
                        "location": step.get("location", []),
                    }
                    for step in steps
                ],
                "geometry": geojson["features"][0]["geometry"],
            }

        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Malformed ORS response: missing expected keys - {e}")
            return None
