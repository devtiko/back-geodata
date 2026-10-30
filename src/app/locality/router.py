from typing import Annotated

from fastapi import APIRouter, Depends

from src.app.locality.dependencies import LocalityId, LocalityServiceDep
from src.app.locality.schemas import (
  LocalityFilters,
  LocalityPaginatedResponse,
  LocalityResponse,
)
from src.common.schemas import PaginationParams

router = APIRouter(prefix="/localities", tags=["localities"])


@router.get("/", response_model=LocalityPaginatedResponse)
def list_localities(
  filters: Annotated[LocalityFilters, Depends()],
  pagination: Annotated[PaginationParams, Depends()],
  service: LocalityServiceDep,
) -> LocalityPaginatedResponse:
  return service.list(filters, pagination)


@router.get("/{locality_id}", response_model=LocalityResponse)
def get_locality(
  locality_id: LocalityId, service: LocalityServiceDep
) -> LocalityResponse:
  return service.get(locality_id)
