from typing import Annotated

from fastapi import Depends

from src.app.geocoding.repository import GeocodingRepository
from src.app.geocoding.service import GeocodingService
from src.database.session import DbSession


def get_geocoding_service(db: DbSession) -> GeocodingService:
  return GeocodingService(GeocodingRepository(db))


GeocodingServiceDep = Annotated[GeocodingService, Depends(get_geocoding_service)]
