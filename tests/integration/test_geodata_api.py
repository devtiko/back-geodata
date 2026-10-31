import pytest

pytestmark = pytest.mark.integration


def test_state_endpoint_reads_from_postgis_database(client, seed_geodata) -> None:
  response = client.get(f"/api/v1/states/{seed_geodata['state_id']}")

  assert response.status_code == 200
  assert response.json()["name"] == "Córdoba"


def test_list_endpoint_returns_filtered_pagination(client, seed_geodata) -> None:
  response = client.get(
    "/api/v1/localities",
    params={"search": "villa", "page": 2, "page_size": 2},
  )

  assert response.status_code == 200
  body = response.json()
  assert [item["id"] for item in body["items"]] == ["910010003", "910010004"]
  assert body["meta"]["total_count"] == 4
  assert body["meta"]["page"] == 2


def test_nearby_and_reverse_endpoints_use_spatial_queries(client, seed_geodata) -> None:
  nearby = client.get(
    "/api/v1/localities/nearby",
    params={"lat": 4.6, "lon": -74.1, "radius_km": 2},
  )
  reverse = client.get("/api/v1/geocoding/reverse", params={"lat": 4.6, "lon": -74.1})

  assert nearby.status_code == 200
  assert nearby.json()["meta"]["total_count"] == 2
  assert nearby.json()["items"][0]["locality"]["id"] == seed_geodata["locality_id"]
  assert reverse.status_code == 200
  assert reverse.json()["locality"]["id"] == seed_geodata["locality_id"]


def test_geocoding_search_endpoint_uses_unaccent(client, seed_geodata) -> None:
  response = client.get("/api/v1/geocoding", params={"query": "cordoba"})

  assert response.status_code == 200
  body = response.json()
  assert body["meta"]["total_count"] == 1
  assert body["items"][0]["type"] == "state"
  assert body["items"][0]["state"]["id"] == seed_geodata["state_id"]


def test_api_returns_not_found_for_unknown_state(client) -> None:
  response = client.get("/api/v1/states/99")

  assert response.status_code == 404
  assert response.json()["detail"] == "State not found"
