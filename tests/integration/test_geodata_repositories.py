import pytest
from sqlalchemy import text

from src.app.geocoding.repository import GeocodingRepository
from src.app.geocoding.schemas import GeocodingFilters
from src.app.locality.repository import LocalityRepository
from src.app.locality.schemas import LocalityFilters, NearbyFilters
from src.app.municipality.repository import MunicipalityRepository
from src.app.municipality.schemas import MunicipalityFilters
from src.app.state.repository import StateRepository
from src.app.state.schemas import StateFilters

pytestmark = pytest.mark.integration


def test_migrations_install_postgis_and_unaccent(db_session) -> None:
  postgis_version = db_session.execute(text("SELECT PostGIS_Version()")).scalar_one()
  unaccent_result = db_session.execute(text("SELECT unaccent('Córdoba')")).scalar_one()

  assert postgis_version
  assert unaccent_result == "Cordoba"


def test_state_and_municipality_repositories_filter_and_paginate(
  db_session, seed_geodata
) -> None:
  states = StateRepository(db_session)
  municipalities = MunicipalityRepository(db_session)

  state = states.get_by_id(seed_geodata["state_id"])
  assert state is not None
  assert state.name == "Córdoba"
  assert [state.id for state in states.list(StateFilters(search="cordoba"), 0, 10)] == [
    "91"
  ]
  assert states.count(StateFilters(search="CORDOBA")) == 1

  filters = MunicipalityFilters(state_id="91", search="jose")
  result = municipalities.list(filters, skip=0, limit=1)
  assert [(item.id, item.name) for item in result] == [("91001", "San José")]
  assert municipalities.count(filters) == 1
  assert municipalities.get_by_id("missing") is None


def test_locality_repository_filters_counts_and_gets_records(
  db_session, seed_geodata
) -> None:
  repository = LocalityRepository(db_session)
  filters = LocalityFilters(state_id="91", municipality_id="91001", search="villa")

  records = repository.list(filters, skip=1, limit=2)

  assert [item.id for item in records] == ["910010002", "910010003"]
  assert repository.count(filters) == 4
  locality = repository.get_by_id(seed_geodata["locality_id"])
  assert locality is not None
  assert locality.name == "Villa del Río"
  assert repository.get_by_id("missing") is None


def test_nearby_repository_applies_radius_order_and_pagination(
  db_session, seed_geodata
) -> None:
  repository = LocalityRepository(db_session)
  filters = NearbyFilters(lat=4.6, lon=-74.1, radius_km=2)

  items, total = repository.nearby(filters, skip=0, limit=1)

  assert total == 2
  assert len(items) == 1
  assert items[0].locality.id == seed_geodata["locality_id"]
  assert items[0].distance_km == pytest.approx(0, abs=0.001)


def test_geocoding_search_supports_unaccent_filters_and_total(
  db_session, seed_geodata
) -> None:
  repository = GeocodingRepository(db_session)

  items, total = repository.search(GeocodingFilters(query="cordoba"), skip=0, limit=10)

  assert total == 1
  assert [(item.type, item.id, item.name) for item in items] == [
    ("state", seed_geodata["state_id"], "Córdoba")
  ]

  locality_items, locality_total = repository.search(
    GeocodingFilters(query="villa", municipality_id="91001"), skip=1, limit=2
  )
  assert locality_total == 4
  assert [item.id for item in locality_items] == ["910010002", "910010003"]


def test_reverse_geocoding_matches_geometry_and_nearest_fallback(
  db_session, seed_geodata
) -> None:
  repository = GeocodingRepository(db_session)

  covered = repository.reverse(latitude=4.6, longitude=-74.1)
  assert covered.locality is not None
  assert covered.municipality is not None
  assert covered.state is not None
  assert covered.locality.id == seed_geodata["locality_id"]
  assert covered.municipality.id == seed_geodata["municipality_id"]
  assert covered.state.id == seed_geodata["state_id"]

  near_but_outside_locality = repository.reverse(latitude=4.6, longitude=-74.105)
  assert near_but_outside_locality.locality is not None
  assert near_but_outside_locality.locality.id == seed_geodata["locality_id"]

  municipality_only = repository.reverse(latitude=4.7, longitude=-74.1)
  assert municipality_only.locality is None
  assert municipality_only.municipality is not None
  assert municipality_only.state is not None
  assert municipality_only.municipality.id == seed_geodata["municipality_id"]
  assert municipality_only.state.id == seed_geodata["state_id"]

  no_match = repository.reverse(latitude=0, longitude=0)
  assert no_match.locality is None
  assert no_match.municipality is None
  assert no_match.state is None
