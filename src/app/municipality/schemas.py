from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.common.schemas import PaginatedResponse


class MunicipalityFilters(BaseModel):
  search: str | None = None
  state_id: str | None = None


class MunicipalityResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  state_id: str
  name: str
  created_at: datetime | None = None
  updated_at: datetime | None = None

MunicipalityPaginatedResponse = PaginatedResponse[MunicipalityResponse]
