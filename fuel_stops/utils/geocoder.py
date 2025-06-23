import logging
from typing import Optional, Tuple

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)


class Geocoder:
    def __init__(self):
        self.client = Nominatim(user_agent="fuelstop_geocoder")

    def fetch(self, address: str) -> Optional[Tuple[float, float]]:
        try:
            location = self.client.geocode(address)
            if location:
                return location.Latitude, location.Longitude
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding service error for {address}: {e}")
            print(f"Geocoding service error for {address}: {e}")
        return None
