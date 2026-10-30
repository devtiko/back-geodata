from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.common.schemas import PaginatedResponse


class LocalityFilters(BaseModel):
  search: str | None = None
  state_id: str | None = None
  municipality_id: str | None = None


class LocalityResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  name: str
  state_id: str
  municipality_id: str
  latitud: float | None
  longitud: float | None
  created_at: datetime | None = None
  updated_at: datetime | None = None

LocalityPaginatedResponse = PaginatedResponse[LocalityResponse]
