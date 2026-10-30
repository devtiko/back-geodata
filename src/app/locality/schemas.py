from datetime import datetime

from pydantic import BaseModel

from src.common.schemas import PaginatedResponse


class LocalityFilters(BaseModel):
  search: str | None = None
  state_id: str | None = None
  municipality_id: str | None = None


class LocalityResponse(BaseModel):
  id: str
  name: str
  state_id: str
  municipality_id: str
  latitud: float | None
  longitud: float | None
  created_at: datetime | None = None
  updated_at: datetime | None = None

  class Config:
    from_attributes = True


LocalityPaginatedResponse = PaginatedResponse[LocalityResponse]
