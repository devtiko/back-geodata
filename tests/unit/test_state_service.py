from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from src.app.state.schemas import StateFilters
from src.app.state.service import StateService
from src.common.schemas import PaginationParams


def state(**overrides):
  values = {"id": "01", "name": "Estado", "short_name": "ES"}
  return SimpleNamespace(**(values | overrides))


def test_list_uses_repository_count_when_paginated() -> None:
  repository = Mock()
  repository.list.return_value = [state()]
  repository.count.return_value = 12
  service = StateService(repository)
  filters = StateFilters(search="esta")
  pagination = PaginationParams(page=2, page_size=5)

  result = service.list(filters, pagination)

  repository.list.assert_called_once_with(filters, 5, 5)
  repository.count.assert_called_once_with(filters)
  assert result.items[0].id == "01"
  assert result.meta.total_count == 12
  assert result.meta.page == 2


def test_list_uses_returned_item_count_without_pagination() -> None:
  repository = Mock()
  repository.list.return_value = [state(), state(id="02", name="Otro")]
  service = StateService(repository)
  filters = StateFilters()

  result = service.list(filters, PaginationParams(paginate=False))

  repository.list.assert_called_once_with(filters, None, None)
  repository.count.assert_not_called()
  assert result.meta.total_count == 2


def test_get_returns_state() -> None:
  repository = Mock()
  repository.get_by_id.return_value = state()

  result = StateService(repository).get("01")

  assert result.id == "01"
  assert result.name == "Estado"


def test_get_raises_not_found_when_state_is_missing() -> None:
  repository = Mock()
  repository.get_by_id.return_value = None

  with pytest.raises(HTTPException) as error:
    StateService(repository).get("missing")

  assert error.value.status_code == 404
  assert error.value.detail == "State not found"
