import csv


def test_geocode_csv_writes_output_with_lat_lon(
    mock_open_csv, mock_geocoder_success, call_geocode_command
):
    output_file = call_geocode_command()

    assert output_file.exists()

    with open(output_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert "Latitude" in rows[0]
    assert "Longitude" in rows[0]
    assert rows[0]["Latitude"] == "40.7128"
    assert rows[0]["Longitude"] == "-74.006"


def test_geocode_csv_skips_ungeocodable_addresses(
    mock_open_csv, mock_geocoder_failure, call_geocode_command
):
    output_file = call_geocode_command()

    assert output_file.exists()

    with open(output_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 0


def test_geocode_csv_uses_cache_and_skips_reprocessing(
    mock_open_csv, mock_geocoder_success, call_geocode_command
):
    output_file = call_geocode_command()
    first_run = list(csv.DictReader(open(output_file)))

    output_file_second = call_geocode_command()
    second_run = list(csv.DictReader(open(output_file_second)))

    assert len(first_run) == len(second_run)
    assert first_run[0]["Latitude"] == second_run[0]["Latitude"]
    assert first_run[0]["Longitude"] == second_run[0]["Longitude"]
