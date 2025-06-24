import logging
from typing import Optional, Tuple

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)


class Geocoder:
    def __init__(self):
        self.client = Nominatim(user_agent="fuelstop_geocoder")

    def fetch(self, truckstop_name: str) -> Optional[Tuple[float, float]]:
        """Fetches the geocode for a given truckstop_name.

        Args:
            truckstop_name (str): The truckstop_name to geocode.

        Returns:
            Optional[Tuple[float, float]]: The geocode for the given truckstop_name, or None if the geocoding fails.
        """
        try:
            location = self.client.geocode(truckstop_name)
            if location:
                return location.Latitude, location.Longitude
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding service error for {truckstop_name}: {e}")
        return None
