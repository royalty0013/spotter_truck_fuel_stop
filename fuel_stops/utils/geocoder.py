import logging
from typing import Optional, Tuple

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)


class Geocoder:
    def __init__(self):
        self.client = Nominatim(user_agent="fuelstop_geocoder")

    def fetch(self, address: str) -> Optional[Tuple[float, float]]:
        """Fetches the geocode for a given address.

        Args:
            address (str): The address to geocode.

        Returns:
            Optional[Tuple[float, float]]: The geocode for the given address, or None if the geocoding fails.
        """
        try:
            location = self.client.geocode(address)
            if location:
                return location.Latitude, location.Longitude
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding service error for {address}: {e}")
        return None
