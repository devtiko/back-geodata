from src.app.geocoding.repository import GeocodingRepository
from src.app.geocoding.schemas import (
  GeocodingFilters,
  GeocodingLocalityResult,
  GeocodingMunicipalityResult,
  GeocodingPaginatedResponse,
  GeocodingStateResult,
  ReverseLocality,
  ReverseMunicipality,
  ReverseResponse,
  ReverseState,
)
from src.common.schemas import PaginationParams


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
      ReverseState.model_validate(matches.state) if matches.state is not None else None
    )

    return ReverseResponse(
      latitude=latitude,
      longitude=longitude,
      locality=locality,
      municipality=municipality,
      state=state,
    )

  def search(
    self,
    filters: GeocodingFilters,
    pagination: PaginationParams,
  ) -> GeocodingPaginatedResponse:
    items, total_count = self.repository.search(
      filters=filters,
      skip=pagination.skip,
      limit=pagination.limit,
    )
    results = []
    for item in items:
      if item.type == "locality":
        results.append(
          GeocodingLocalityResult(
            type=item.type,
            locality=ReverseLocality.model_validate(item),
          )
        )
      elif item.type == "municipality":
        results.append(
          GeocodingMunicipalityResult(
            type=item.type,
            municipality=ReverseMunicipality.model_validate(item),
          )
        )
      else:
        results.append(
          GeocodingStateResult(
            type=item.type,
            state=ReverseState.model_validate(item),
          )
        )

    return GeocodingPaginatedResponse.create(
      items=results,
      page=pagination.page,
      page_size=pagination.page_size,
      total_count=total_count,
      paginate=pagination.paginate,
    )
