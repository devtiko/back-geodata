from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.common.schemas import PaginatedResponse


class GeocodingFilters(BaseModel):
  query: str = Field(min_length=1, max_length=200, pattern=r".*\S.*")
  state_id: str | None = Field(default=None, min_length=1, max_length=2)
  municipality_id: str | None = Field(default=None, min_length=1, max_length=5)

  @field_validator("query", mode="before")
  @classmethod
  def strip_query(cls, value: str) -> str:
    return value.strip()


class ReverseState(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  name: str
  short_name: str | None


class ReverseMunicipality(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  name: str


class ReverseLocality(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: str
  name: str
  latitude: float | None
  longitude: float | None


class ReverseResponse(BaseModel):
  latitude: float
  longitude: float
  locality: ReverseLocality | None
  municipality: ReverseMunicipality | None
  state: ReverseState | None


class GeocodingLocalityResult(BaseModel):
  type: Literal["locality"]
  locality: ReverseLocality


class GeocodingMunicipalityResult(BaseModel):
  type: Literal["municipality"]
  municipality: ReverseMunicipality


class GeocodingStateResult(BaseModel):
  type: Literal["state"]
  state: ReverseState


GeocodingResult = Annotated[
  GeocodingLocalityResult | GeocodingMunicipalityResult | GeocodingStateResult,
  Field(discriminator="type"),
]


GeocodingPaginatedResponse = PaginatedResponse[GeocodingResult]
