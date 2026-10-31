from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.common.schemas import PaginatedResponse


class LocalityFilters(BaseModel):
  search: str | None = None
  state_id: str | None = None
  municipality_id: str | None = None


class NearbyFilters(BaseModel):
  latitude: float = Field(alias="lat", ge=-90, le=90)
  longitude: float = Field(alias="lon", ge=-180, le=180)
  radius_km: float = Field(default=5, gt=0, le=25)

  model_config = ConfigDict(populate_by_name=True)


class LocalityResponse(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  name: str
  state_id: str
  municipality_id: str
  latitude: float | None
  longitude: float | None
  created_at: datetime | None = None
  updated_at: datetime | None = None


class NearbyLocality(BaseModel):
  locality: LocalityResponse
  distance_km: float


NearbyLocalitiesResponse = PaginatedResponse[NearbyLocality]

LocalityPaginatedResponse = PaginatedResponse[LocalityResponse]
