from src.common.schemas import PaginatedResponse, PaginationParams


def test_pagination_params_calculates_skip_and_limit() -> None:
  params = PaginationParams(page=3, page_size=20)

  assert params.skip == 40
  assert params.limit == 20


def test_pagination_params_disables_skip_and_limit_without_pagination() -> None:
  params = PaginationParams(page=3, page_size=20, paginate=False)

  assert params.skip is None
  assert params.limit is None


def test_paginated_response_creates_page_metadata() -> None:
  response = PaginatedResponse[int].create(
    items=[1, 2], page=2, page_size=2, total_count=5
  )

  assert response.items == [1, 2]
  assert response.meta.page == 2
  assert response.meta.page_size == 2
  assert response.meta.total_count == 5
  assert response.meta.total_pages == 3
  assert response.meta.has_next_page is True
  assert response.meta.has_prev_page is True


def test_paginated_response_metadata_without_pagination() -> None:
  response = PaginatedResponse[int].create(
    items=[1, 2], page=4, page_size=10, total_count=50, paginate=False
  )

  assert response.meta.page == 1
  assert response.meta.page_size == 2
  assert response.meta.total_pages == 1
  assert response.meta.has_next_page is False
  assert response.meta.has_prev_page is False
