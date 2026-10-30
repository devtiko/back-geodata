from datetime import datetime

from pydantic import BaseModel

from src.common.schemas import PaginatedResponse


class MunicipalityFilters(BaseModel):
  search: str | None = None
  state_id: str | None = None


class MunicipalityResponse(BaseModel):
  id: str
  state_id: str
  name: str
  created_at: datetime | None = None
  updated_at: datetime | None = None

  class Config:
    from_attributes = True


MunicipalityPaginatedResponse = PaginatedResponse[MunicipalityResponse]
