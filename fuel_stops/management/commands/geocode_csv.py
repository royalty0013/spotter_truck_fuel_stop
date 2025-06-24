import csv
import logging
import time
from pathlib import Path

from django.core.management.base import BaseCommand

from fuel_stops.utils.geocode_cache import GeocodeCache
from fuel_stops.utils.geocoder import Geocoder

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Geocode addresses from CSV, skipping duplicates and already-processed entries"
    )

    def add_arguments(self, parser):
        parser.add_argument("--input", type=str, help="Path to input CSV")
        parser.add_argument(
            "--output",
            type=str,
            default="data/fuelstops_address_geocoded.csv",
            help="Path to output CSV",
        )
        parser.add_argument(
            "--cache",
            type=str,
            default="data/geocode_cache.json",
            help="Path to geocode cache file",
        )

    def handle(self, *args, **kwargs):
        """Handles the geocoding of addresses from a CSV file."""
        input_path = Path(kwargs.get("input", "data/fuel-prices-for-be-assessment.csv"))
        output_path = Path(kwargs.get("output", "data/fuelstops_address_geocoded.csv"))
        cache_path = Path(kwargs.get("cache", "data/geocode_cache.json"))

        seen_ids = set()
        cache = GeocodeCache(cache_path)
        geocoder = Geocoder()

        with input_path.open(newline="", encoding="utf-8") as infile, output_path.open(
            "w", newline="", encoding="utf-8"
        ) as outfile:
            reader = csv.DictReader(infile)
            fieldnames = (
                reader.fieldnames + ["Latitude", "Longitude"]
                if reader.fieldnames
                else []
            )
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                truckstop_id = row["OPIS Truckstop ID"].strip()
                if truckstop_id in seen_ids:
                    continue
                seen_ids.add(truckstop_id)

                cached = cache.get(truckstop_id)
                if cached:
                    row["Latitude"], row["Longitude"] = cached
                    writer.writerow(row)
                    continue

                truckstop_name = row["Truckstop Name"].strip()
                coordinate = geocoder.fetch(truckstop_name)
                if coordinate:
                    lat, lon = coordinate
                    cache.set(truckstop_id, lat, lon)
                    row["Latitude"], row["Longitude"] = lat, lon
                    writer.writerow(row)
                    time.sleep(1)
                else:
                    continue

        self.stdout.write(
            self.style.SUCCESS(f"Geocoding complete. Output saved to: {output_path}")
        )
