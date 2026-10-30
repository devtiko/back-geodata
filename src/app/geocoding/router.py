from typing import Annotated

from fastapi import APIRouter, Query

from src.app.geocoding.dependencies import GeocodingServiceDep
from src.app.geocoding.schemas import ReverseResponse

router = APIRouter(prefix="/geocoding", tags=["geocoding"])


@router.get("/reverse", response_model=ReverseResponse)
def reverse(
  latitude: Annotated[float, Query(alias="lat", ge=-90, le=90)],
  longitude: Annotated[float, Query(alias="lon", ge=-180, le=180)],
  service: GeocodingServiceDep,
) -> ReverseResponse:
  return service.reverse(latitude, longitude)
