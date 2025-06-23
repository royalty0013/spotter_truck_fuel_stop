import csv
import json
import logging
import os
import time

from django.core.management.base import BaseCommand
from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim

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
        input_path = kwargs.get("input", "data/fuel-prices-for-be-assessment.csv")
        output_path = kwargs.get("output", "data/fuelstops_address_geocoded.csv")
        cache_path = kwargs.get("cache", "data/geocode_cache.json")

        seen_ids = set()
        fieldnames = None

        # Load existing cache
        cache = {}
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                try:
                    cache = json.load(f)
                except json.JSONDecodeError:
                    self.stdout.write(
                        self.style.WARNING(
                            "Cache file is empty or invalid. Starting fresh."
                        )
                    )
        geolocator = Nominatim(user_agent="fuelstop_geocoder")

        with open(input_path, newline="", encoding="utf-8") as infile, open(
            output_path, "w", newline="", encoding="utf-8"
        ) as outfile:

            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ["latitude", "longitude"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                truckstop_id = row["OPIS Truckstop ID"].strip()
                if truckstop_id in seen_ids:
                    continue  # Skip duplicates
                seen_ids.add(truckstop_id)

                # If already in cache, write cached result
                if truckstop_id in cache:
                    lat, lon = cache[truckstop_id]
                    row["latitude"] = lat
                    row["longitude"] = lon
                    writer.writerow(row)
                    continue

                # Build address string
                truckstop_name = row["Truckstop Name"].strip()

                try:
                    location = geolocator.geocode(truckstop_name)
                    if location:
                        lat = location.latitude
                        lon = location.longitude
                        cache[truckstop_id] = [lat, lon]

                        # Write cache incrementally
                        with open(cache_path, "w") as f:
                            json.dump(cache, f)

                        row["latitude"] = lat
                        row["longitude"] = lon
                    else:
                        continue
                    print(row)
                    print("***********************************")
                    writer.writerow(row)
                    time.sleep(1)  # Rate limit

                except (GeocoderTimedOut, GeocoderServiceError) as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Geocoding error for {truckstop_name}: {str(e)}"
                        )
                    )
                    continue
                except Exception as e:
                    logger.error(f"Error processing {truckstop_id}: {e}")
                    self.stdout.write(self.style.ERROR(f"Unexpected error: {e}"))
                    continue

        self.stdout.write(
            self.style.SUCCESS("Geocoding complete. Output saved to %s" % output_path)
        )
