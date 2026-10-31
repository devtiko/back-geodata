from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from src.app.locality.schemas import LocalityFilters, NearbyFilters
from src.app.locality.service import LocalityService
from src.common.schemas import PaginationParams


def locality(**overrides):
  values = {
    "id": "010010001",
    "name": "Localidad",
    "state_id": "01",
    "municipality_id": "01001",
    "latitude": 4.6,
    "longitude": -74.1,
  }
  return SimpleNamespace(**(values | overrides))


def test_list_uses_repository_count_when_paginated() -> None:
  repository = Mock()
  repository.list.return_value = [locality()]
  repository.count.return_value = 15
  service = LocalityService(repository)
  filters = LocalityFilters(state_id="01")
  pagination = PaginationParams(page=2, page_size=5)

  result = service.list(filters, pagination)

  repository.list.assert_called_once_with(filters, 5, 5)
  repository.count.assert_called_once_with(filters)
  assert result.items[0].id == "010010001"
  assert result.meta.total_count == 15


def test_list_uses_returned_item_count_without_pagination() -> None:
  repository = Mock()
  repository.list.return_value = [locality()]
  service = LocalityService(repository)
  filters = LocalityFilters()

  result = service.list(filters, PaginationParams(paginate=False))

  repository.list.assert_called_once_with(filters, None, None)
  repository.count.assert_not_called()
  assert result.meta.total_count == 1


def test_get_returns_locality() -> None:
  repository = Mock()
  repository.get_by_id.return_value = locality()

  result = LocalityService(repository).get("010010001")

  assert result.id == "010010001"
  assert result.name == "Localidad"


def test_get_raises_not_found_when_locality_is_missing() -> None:
  repository = Mock()
  repository.get_by_id.return_value = None

  with pytest.raises(HTTPException) as error:
    LocalityService(repository).get("missing")

  assert error.value.status_code == 404
  assert error.value.detail == "Locality not found"


def test_nearby_maps_items_and_rounds_distance() -> None:
  repository = Mock()
  repository.nearby.return_value = (
    [SimpleNamespace(locality=locality(), distance_km=1.236)],
    1,
  )
  service = LocalityService(repository)
  filters = NearbyFilters(lat=4.6, lon=-74.1, radius_km=3)
  pagination = PaginationParams(page=1, page_size=10)

  result = service.nearby(filters, pagination)

  repository.nearby.assert_called_once_with(
    filters=filters, skip=0, limit=10
  )
  assert result.items[0].locality.id == "010010001"
  assert result.items[0].distance_km == 1.24
  assert result.meta.total_count == 1
