from src.app.geocoding.repository import GeocodingRepository
from src.app.geocoding.schemas import (
  ReverseLocality,
  ReverseMunicipality,
  ReverseResponse,
  ReverseState,
)


class GeocodingService:
  def __init__(self, repository: GeocodingRepository) -> None:
    self.repository = repository

  def reverse(self, latitude: float, longitude: float) -> ReverseResponse:
    matches = self.repository.reverse(latitude, longitude)
    locality = (
      ReverseLocality.model_validate(matches.locality)
      if matches.locality is not None
      else None
    )
    municipality = (
      ReverseMunicipality.model_validate(matches.municipality)
      if matches.municipality is not None
      else None
    )
    state = (
      ReverseState.model_validate(matches.state)
      if matches.state is not None
      else None
    )

    return ReverseResponse(
      latitude=latitude,
      longitude=longitude,
      locality=locality,
      municipality=municipality,
      state=state,
    )
