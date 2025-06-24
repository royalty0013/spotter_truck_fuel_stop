# fuel_stops/tests/conftest.py

import csv
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_command(mock_stdout, mock_stderr):
    """Mock Django management command object with style and stdout/stderr."""
    cmd = Mock()
    cmd.stdout = mock_stdout
    cmd.stderr = mock_stderr
    cmd.style.SUCCESS = lambda x: x
    cmd.style.NOTICE = lambda x: x
    cmd.style.WARNING = lambda x: x
    cmd.style.ERROR = lambda x: x
    return cmd


@pytest.fixture
def sample_input_rows():
    return [
        {
            "OPIS Truckstop ID": 1001,
            "Truckstop Name": "Test Stop 1",
            "Address": "123 Main St",
            "City": "Springfield",
            "State": "IL",
            "Rack ID": "123",
            "Retail Price": 3.50,
        },
        {
            "OPIS Truckstop ID": 1002,
            "Truckstop Name": "Test Stop 2",
            "Address": "456 Oak Ave",
            "City": "Riverside",
            "State": "CA",
            "Rack ID": "456",
            "Retail Price": 4.50,
        },
    ]


@pytest.fixture
def sample_csv_data():
    return [
        {
            "OPIS Truckstop ID": "1001",
            "Truckstop Name": "Test Stop 1",
            "Address": "123 Main St",
            "City": "Springfield",
            "State": "IL",
            "Rack ID": "901",
            "Retail Price": "3.199",
            "Latitude": "40.7128",
            "Longitude": "-74.0060",
        },
        {
            "OPIS Truckstop ID": "1002",
            "Truckstop Name": "Test Stop 2",
            "Address": "456 Oak Ave",
            "City": "Riverside",
            "State": "CA",
            "Rack ID": "902",
            "Retail Price": "3.299",
            "Latitude": "34.0522",
            "Longitude": "-118.0775",
        },
    ]


@pytest.fixture
def duplicate_csv_data():
    return [
        {
            "OPIS Truckstop ID": "1001",
            "Truckstop Name": "Test Stop 1",
            "Address": "123 Main St",
            "City": "Springfield",
            "State": "IL",
            "Rack ID": "901",
            "Retail Price": "3.199",
            "Latitude": "40.7128",
            "Longitude": "-74.0060",
        },
        {
            "OPIS Truckstop ID": "1001",  # Duplicate
            "Truckstop Name": "Test Stop 1 (duplicate)",
            "Address": "Same Address",
            "City": "Springfield",
            "State": "IL",
            "Rack ID": "901",
            "Retail Price": "3.199",
            "Latitude": "40.7128",
            "Longitude": "-74.0060",
        },
    ]


@pytest.fixture
def mock_stdout():
    return Mock(write=Mock())


@pytest.fixture
def mock_stderr():
    return Mock(write=Mock())


@pytest.fixture
def mock_open_csv(sample_input_rows, tmp_path):
    """Fixture that mocks reading from input CSV"""
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"
    cache_file = tmp_path / "cache.json"

    # Write sample input data
    with open(input_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sample_input_rows[0].keys())
        writer.writeheader()
        writer.writerows(sample_input_rows)

    return {
        "input_file": input_file,
        "output_file": output_file,
        "cache_file": cache_file,
    }


@pytest.fixture
def mock_geocoder_success():
    with patch("fuel_stops.utils.geocoder.Geocoder.fetch") as mock_fetch:
        mock_fetch.return_value = (40.7128, -74.0060)  # Simulate success
        yield mock_fetch


@pytest.fixture
def mock_geocoder_failure():
    with patch("fuel_stops.utils.geocoder.Geocoder.fetch") as mock_fetch:
        mock_fetch.return_value = None
        yield mock_fetch


@pytest.fixture
def call_geocode_command(mock_open_csv):
    def _call(**kwargs):
        input_file = kwargs.get("input", mock_open_csv["input_file"])
        output_file = kwargs.get("output", mock_open_csv["output_file"])
        cache_file = kwargs.get("cache", mock_open_csv["cache_file"])

        from django.core.management import call_command

        call_command(
            "geocode_csv",
            input=str(input_file),
            output=str(output_file),
            cache=str(cache_file),
        )
        return output_file

    return _call
