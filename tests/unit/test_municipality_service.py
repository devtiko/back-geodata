from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from src.app.municipality.schemas import MunicipalityFilters
from src.app.municipality.service import MunicipalityService
from src.common.schemas import PaginationParams


def municipality(**overrides):
  values = {"id": "01001", "state_id": "01", "name": "Municipio"}
  return SimpleNamespace(**(values | overrides))


def test_list_uses_repository_count_when_paginated() -> None:
  repository = Mock()
  repository.list.return_value = [municipality()]
  repository.count.return_value = 8
  service = MunicipalityService(repository)
  filters = MunicipalityFilters(state_id="01")
  pagination = PaginationParams(page=2, page_size=3)

  result = service.list(filters, pagination)

  repository.list.assert_called_once_with(filters, 3, 3)
  repository.count.assert_called_once_with(filters)
  assert result.items[0].id == "01001"
  assert result.meta.total_count == 8


def test_list_uses_returned_item_count_without_pagination() -> None:
  repository = Mock()
  repository.list.return_value = [municipality(), municipality(id="01002")]
  service = MunicipalityService(repository)
  filters = MunicipalityFilters()

  result = service.list(filters, PaginationParams(paginate=False))

  repository.list.assert_called_once_with(filters, None, None)
  repository.count.assert_not_called()
  assert result.meta.total_count == 2


def test_get_returns_municipality() -> None:
  repository = Mock()
  repository.get_by_id.return_value = municipality()

  result = MunicipalityService(repository).get("01001")

  assert result.id == "01001"
  assert result.state_id == "01"


def test_get_raises_not_found_when_municipality_is_missing() -> None:
  repository = Mock()
  repository.get_by_id.return_value = None

  with pytest.raises(HTTPException) as error:
    MunicipalityService(repository).get("missing")

  assert error.value.status_code == 404
  assert error.value.detail == "Municipality not found"
