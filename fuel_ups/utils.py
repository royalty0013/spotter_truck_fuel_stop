import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)


class GeocodeCache:
    def __init__(self, path: Path):
        self.path = path
        self.data: Dict[str, Tuple[float, float]] = self._load()

    def _load(self) -> Dict[str, Tuple[float, float]]:
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("Cache file is empty or invalid. Starting fresh.")
            print("Cache file is empty or invalid. Starting fresh.")
            return {}

    def get(self, key: str) -> Optional[Tuple[float, float]]:
        return self.data.get(key)

    def set(self, key: str, lat: float, lon: float):
        self.data[key] = (lat, lon)
        self.save()

    def save(self):
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)


class Geocoder:
    def __init__(self):
        self.client = Nominatim(user_agent="fuelstop_geocoder")

    def fetch(self, address: str) -> Optional[Tuple[float, float]]:
        try:
            location = self.client.geocode(address)
            if location:
                return location.latitude, location.longitude
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding service error for {address}: {e}")
            print(f"Geocoding service error for {address}: {e}")
        return None
