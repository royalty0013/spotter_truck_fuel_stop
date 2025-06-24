import logging
from pathlib import Path

from django.core.management.base import BaseCommand

from fuel_stops.services.import_create_fuelstop_service import (
    ImportCreateFuelStopService,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Bulk import fuel stops from a geocoded CSV file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            type=str,
            default="data/fuelstops_address_geocoded.csv",
            help="Path to the geocoded CSV file.",
        )

    def handle(self, *args, **options):
        """Handles the import of fuel stops from a geocoded CSV file."""
        file_path = Path(options["input"])

        self.stdout.write(self.style.SUCCESS(f"Reading CSV file: {file_path}"))

        importer = ImportCreateFuelStopService(file_path)

        try:
            count = importer.import_csv(self)
            self.stdout.write(
                self.style.SUCCESS(f"Successfully imported {count} fuel stops.")
            )
        except FileNotFoundError as e:
            self.stderr.write(self.style.ERROR(f"File error: {e}"))
        except ValueError as e:
            self.stderr.write(self.style.ERROR(f"CSV validation error: {e}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Unexpected error: {e}"))
            logger.exception("Fatal error during fuel stop import.")
