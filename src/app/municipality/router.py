from typing import Annotated

from fastapi import APIRouter, Depends

from src.app.municipality.dependencies import (
  MunicipalityId,
  MunicipalityServiceDep,
)
from src.app.municipality.schemas import (
  MunicipalityFilters,
  MunicipalityPaginatedResponse,
  MunicipalityResponse,
)
from src.common.schemas import PaginationParams

router = APIRouter(prefix="/municipalities", tags=["municipalities"])


@router.get("/", response_model=MunicipalityPaginatedResponse)
def list_municipalities(
  filters: Annotated[MunicipalityFilters, Depends()],
  pagination: Annotated[PaginationParams, Depends()],
  service: MunicipalityServiceDep,
) -> MunicipalityPaginatedResponse:
  return service.list(filters, pagination)


@router.get("/{municipality_id}", response_model=MunicipalityResponse)
def get_municipality(
  municipality_id: MunicipalityId, service: MunicipalityServiceDep
) -> MunicipalityResponse:
  return service.get(municipality_id)
