from fastapi import HTTPException, status

from src.app.state.repository import StateRepository
from src.app.state.schemas import StateFilters, StatePaginatedResponse, StateResponse
from src.common.schemas import PaginationParams


class StateService:
  def __init__(self, repository: StateRepository) -> None:
    self.repository = repository

  def list(
    self, filters: StateFilters, pagination: PaginationParams
  ) -> StatePaginatedResponse:

    items = self.repository.list(
      filters=filters, skip=pagination.skip, limit=pagination.limit
    )

    if pagination.paginate:
      total_count = self.repository.count(filters=filters)
    else:
      total_count = len(items)

    return StatePaginatedResponse.create(
      items=[StateResponse.model_validate(item) for item in items],
      page=pagination.page,
      page_size=pagination.page_size,
      total_count=total_count,
      paginate=pagination.paginate,
    )

  def get(self, state_id: str) -> StateResponse:
    state = self.repository.get_by_id(state_id)
    if state is None:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="State not found"
      )
    return StateResponse.model_validate(state)
