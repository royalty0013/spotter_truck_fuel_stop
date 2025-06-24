import csv
from unittest.mock import patch

import pytest

from fuel_stops.models import FuelStop
from fuel_stops.services.import_create_fuelstop_service import ImportCreateFuelStop


@pytest.mark.django_db
def test_bulk_create_valid_csv_creates_fuelstops(
    sample_csv_data, mock_command, tmp_path
):
    """Test bulk creating valid CSV creates new fuel stops."""
    csv_file = tmp_path / "test.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sample_csv_data[0].keys())
        writer.writeheader()
        writer.writerows(sample_csv_data)

    importer = ImportCreateFuelStop(csv_file)
    count = importer.import_csv(mock_command)

    assert count == 2
    assert FuelStop.objects.count() == 2


@pytest.mark.django_db
def test_duplicate_ids_skipped(duplicate_csv_data, mock_command, tmp_path):
    """Test that duplicate OPIS Truckstop IDs are skipped."""
    csv_file = tmp_path / "duplicates.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=duplicate_csv_data[0].keys())
        writer.writeheader()
        writer.writerows(duplicate_csv_data)

    importer = ImportCreateFuelStop(csv_file)
    count = importer.import_csv(mock_command)

    assert count == 1
    assert FuelStop.objects.count() == 1


@patch("fuel_stops.services.import_create_fuelstop_service.csv.DictReader")
def test_missing_required_columns_raises_error(mock_dictreader, mock_command, tmp_path):
    """Test ValueError raised when required columns are missing."""
    mock_dictreader.return_value.fieldnames = ["OPIS Truckstop ID", "Truckstop Name"]
    csv_file = tmp_path / "bad.csv"
    csv_file.touch()

    importer = ImportCreateFuelStop(csv_file)
    with pytest.raises(ValueError):
        importer.import_csv(mock_command)
