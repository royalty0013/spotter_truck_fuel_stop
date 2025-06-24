import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class GeocodeCache:
    def __init__(self, path: Path):
        self.path = path
        self.data: Dict[str, Tuple[float, float]] = self._load()

    def _load(self) -> Dict[str, Tuple[float, float]]:
        """Loads the geocode cache from a JSON file."""
        if not self.path.exists():
            return {}
        try:
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning("Cache file is empty or invalid. Starting fresh.")
            return {}

    def get(self, key: str) -> Optional[Tuple[float, float]]:
        """Gets the geocode for a given key."""
        return self.data.get(key)

    def set(self, key: str, lat: float, lon: float):
        """Sets the geocode for a given key."""
        self.data[key] = (lat, lon)
        self.save()

    def save(self):
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
