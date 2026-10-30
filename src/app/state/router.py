from typing import Annotated

from fastapi import APIRouter, Depends

from src.app.state.dependencies import StateId, StateServiceDep
from src.app.state.schemas import StateFilters, StatePaginatedResponse, StateResponse
from src.common.schemas import PaginationParams

router = APIRouter(prefix="/states", tags=["states"])


@router.get("", response_model=StatePaginatedResponse)
def list_states(
  filters: Annotated[StateFilters, Depends()],
  pagination: Annotated[PaginationParams, Depends()],
  service: StateServiceDep,
) -> StatePaginatedResponse:
  return service.list(filters, pagination)


@router.get("/{state_id}", response_model=StateResponse)
def get_state(state_id: StateId, service: StateServiceDep) -> StateResponse:
  return service.get(state_id)
