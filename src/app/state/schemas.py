from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.common.schemas import PaginatedResponse


class StateFilters(BaseModel):
  search: str | None = None


class StateResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  name: str
  short_name: str | None
  created_at: datetime | None = None
  updated_at: datetime | None = None

StatePaginatedResponse = PaginatedResponse[StateResponse]
