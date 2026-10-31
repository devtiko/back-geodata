from types import SimpleNamespace
from unittest.mock import Mock

from src.app.geocoding.schemas import (
  GeocodingFilters,
  GeocodingLocalityResult,
  GeocodingMunicipalityResult,
  GeocodingStateResult,
)
from src.app.geocoding.service import GeocodingService
from src.common.schemas import PaginationParams


def entities():
  state = SimpleNamespace(id="01", name="Estado", short_name="ES")
  municipality = SimpleNamespace(id="01001", name="Municipio")
  locality = SimpleNamespace(
    id="010010001",
    name="Localidad",
    latitude=4.6,
    longitude=-74.1,
  )
  return state, municipality, locality


def test_reverse_maps_all_matched_entities() -> None:
  repository = Mock()
  state, municipality, locality = entities()
  repository.reverse.return_value = SimpleNamespace(
    state=state, municipality=municipality, locality=locality
  )

  result = GeocodingService(repository).reverse(4.6, -74.1)

  repository.reverse.assert_called_once_with(4.6, -74.1)
  assert result.latitude == 4.6
  assert result.longitude == -74.1
  assert result.locality is not None
  assert result.municipality is not None
  assert result.state is not None
  assert result.locality.id == "010010001"
  assert result.municipality.id == "01001"
  assert result.state.id == "01"


def test_reverse_handles_no_matches() -> None:
  repository = Mock()
  repository.reverse.return_value = SimpleNamespace(
    state=None, municipality=None, locality=None
  )

  result = GeocodingService(repository).reverse(0, 0)

  assert result.locality is None
  assert result.municipality is None
  assert result.state is None


def test_search_maps_results_by_type_and_paginates() -> None:
  repository = Mock()
  state, municipality, locality = entities()
  rows = [
    SimpleNamespace(type="locality", **locality.__dict__),
    SimpleNamespace(type="municipality", **municipality.__dict__),
    SimpleNamespace(type="state", **state.__dict__),
  ]
  repository.search.return_value = (rows, 12)
  service = GeocodingService(repository)
  filters = GeocodingFilters(query="Lugar", state_id="01")
  pagination = PaginationParams(page=2, page_size=5)

  result = service.search(filters, pagination)

  repository.search.assert_called_once_with(filters=filters, skip=5, limit=5)
  assert [item.type for item in result.items] == [
    "locality",
    "municipality",
    "state",
  ]
  locality_result, municipality_result, state_result = result.items
  assert isinstance(locality_result, GeocodingLocalityResult)
  assert isinstance(municipality_result, GeocodingMunicipalityResult)
  assert isinstance(state_result, GeocodingStateResult)
  assert locality_result.locality.id == "010010001"
  assert municipality_result.municipality.id == "01001"
  assert state_result.state.id == "01"
  assert result.meta.total_count == 12
  assert result.meta.page == 2
