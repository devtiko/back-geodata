from datetime import datetime

from pydantic import BaseModel

from src.common.schemas import PaginatedResponse


class StateFilters(BaseModel):
  search: str | None = None


class StateResponse(BaseModel):
  id: str
  name: str
  short_name: str | None
  created_at: datetime | None = None
  updated_at: datetime | None = None

  class Config:
    from_attributes = True


StatePaginatedResponse = PaginatedResponse[StateResponse]
