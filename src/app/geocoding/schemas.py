from pydantic import BaseModel, ConfigDict


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
