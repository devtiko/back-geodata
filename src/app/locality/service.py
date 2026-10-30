from fastapi import HTTPException, status

from src.app.locality.repository import LocalityRepository
from src.app.locality.schemas import (
  LocalityFilters,
  LocalityPaginatedResponse,
  LocalityResponse,
)
from src.common.schemas import PaginationParams


class LocalityService:
  def __init__(self, repository: LocalityRepository) -> None:
    self.repository = repository

  def list(
    self, filters: LocalityFilters, pagination: PaginationParams
  ) -> LocalityPaginatedResponse:
    items = self.repository.list(filters, pagination.skip, pagination.limit)
    total_count = self.repository.count(filters) if pagination.paginate else len(items)
    return LocalityPaginatedResponse.create(
      items=[LocalityResponse.model_validate(item) for item in items],
      page=pagination.page,
      page_size=pagination.page_size,
      total_count=total_count,
      paginate=pagination.paginate,
    )

  def get(self, locality_id: str) -> LocalityResponse:
    locality = self.repository.get_by_id(locality_id)
    if locality is None:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Locality not found"
      )
    return LocalityResponse.model_validate(locality)
