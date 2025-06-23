import csv
import logging
from pathlib import Path
from typing import List, Optional

from django.contrib.gis.geos import Point

from fuel_stops.models import FuelStop

logger = logging.getLogger(__name__)


REQUIRED_FIELDS = [
    "OPIS Truckstop ID",
    "Truckstop Name",
    "Address",
    "City",
    "State",
    "Rack ID",
    "Retail Price",
    "Latitude",
    "Longitude",
]

BATCH_SIZE = 500


class FuelStopImporter:
    """Handles the bulk creation of FuelStop instances from a CSV file."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.seen_ids = set()
        self.created_count = 0

    def import_csv(self, command) -> int:
        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")

        with self.file_path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            if not all(field in reader.fieldnames for field in REQUIRED_FIELDS):
                raise ValueError("CSV is missing one or more required columns")

            batch: List[FuelStop] = []

            for row in reader:
                truckstop_id = row["OPIS Truckstop ID"].strip()
                if truckstop_id in self.seen_ids:
                    continue
                self.seen_ids.add(truckstop_id)

                instance = self._build_instance(row)
                if instance:
                    batch.append(instance)

                if len(batch) >= BATCH_SIZE:
                    self._commit_batch(batch, command)
                    batch.clear()

            if batch:
                self._commit_batch(batch, command)

        return self.created_count

    def _build_instance(self, row: dict) -> Optional[FuelStop]:
        try:
            lat = float(row.get("Latitude", "") or 0)
            lon = float(row.get("Longitude", "") or 0)
            point = Point(lon, lat) if lat and lon else None
        except (ValueError, TypeError):
            point = None

        try:
            retail_price = float(row.get("Retail Price") or 0.0)
        except (ValueError, TypeError):
            retail_price = 0.0

        return FuelStop(
            opis_truckstop=row["OPIS Truckstop ID"].strip(),
            truckstop_name=row["Truckstop Name"].strip(),
            address=row.get("Address", ""),
            city=row.get("City", ""),
            state=row.get("State", ""),
            rack_id=row["Rack ID"].strip(),
            retail_price=retail_price,
            point=point,
        )

    def _commit_batch(self, fuelstops: List[FuelStop], command) -> None:
        existing_ids = set(
            FuelStop.objects.filter(
                opis_truckstop__in=[f.opis_truckstop for f in fuelstops]
            ).values_list("opis_truckstop", flat=True)
        )

        new_fuelstops = [
            fuelstop
            for fuelstop in fuelstops
            if fuelstop.opis_truckstop not in existing_ids
        ]

        if new_fuelstops:
            FuelStop.objects.bulk_create(new_fuelstops)
            command.stdout.write(
                command.style.NOTICE(f"Created {len(new_fuelstops)} new fuel stops.")
            )
            self.created_count += len(new_fuelstops)
        else:
            command.stdout.write(
                command.style.WARNING("No new fuel stops in this batch.")
            )
