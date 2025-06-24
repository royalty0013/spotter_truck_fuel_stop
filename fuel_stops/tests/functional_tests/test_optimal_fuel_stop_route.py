import http
from decimal import Decimal
from unittest.mock import patch

from rest_framework.test import APIClient

from fuel_stops.services.route_optimizer_service import RouteOptimizerService

client = APIClient()


def test_valid_input_returns_success(
    sample_valid_data, mock_ors_client, mock_optimizer_service
):
    response = client.post("/api/fuel-stops/", data=sample_valid_data, format="json")

    assert response.status_code == http.HTTPStatus.OK
    assert "total_cost" in response.data
    assert "fuel_stops" in response.data
    assert "map_data" in response.data

    assert response.data["total_cost"] == Decimal("148.50")
    assert len(response.data["fuel_stops"]) == 1
    assert response.data["fuel_stops"][0]["retail_price"] == Decimal("3.00")


def test_invalid_serializer_returns_bad_request(sample_invalid_data):

    response = client.post("/api/fuel-stops/", data=sample_invalid_data)

    assert response.status_code == http.HTTPStatus.BAD_REQUEST
    assert "start_lat must be between -90 and 90." in response.data["error"]


def test_fuel_stop_not_found_returns_500(sample_valid_data):
    with patch.object(
        RouteOptimizerService, "find_nearest_fuel_stop", return_value=None
    ):
        response = client.post("/api/fuel-stops/", data=sample_valid_data)

    assert response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.data == {"error": "Route optimization failed"}
