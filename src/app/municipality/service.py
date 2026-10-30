from fastapi import HTTPException, status

from src.app.municipality.repository import MunicipalityRepository
from src.app.municipality.schemas import (
  MunicipalityFilters,
  MunicipalityPaginatedResponse,
  MunicipalityResponse,
)
from src.common.schemas import PaginationParams


class MunicipalityService:
  def __init__(self, repository: MunicipalityRepository) -> None:
    self.repository = repository

  def list(
    self, filters: MunicipalityFilters, pagination: PaginationParams
  ) -> MunicipalityPaginatedResponse:
    items = self.repository.list(filters, pagination.skip, pagination.limit)
    total_count = self.repository.count(filters) if pagination.paginate else len(items)

    return MunicipalityPaginatedResponse.create(
      items=[MunicipalityResponse.model_validate(item) for item in items],
      page=pagination.page,
      page_size=pagination.page_size,
      total_count=total_count,
      paginate=pagination.paginate,
    )

  def get(self, municipality_id: str) -> MunicipalityResponse:
    municipality = self.repository.get_by_id(municipality_id)
    if municipality is None:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Municipality not found"
      )
    return MunicipalityResponse.model_validate(municipality)
