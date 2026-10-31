from typing import Annotated

from fastapi import Depends, Path

from src.app.municipality.repository import MunicipalityRepository
from src.app.municipality.service import MunicipalityService
from src.database.session import DbSession


def get_municipality_service(db: DbSession) -> MunicipalityService:
  return MunicipalityService(MunicipalityRepository(db))


MunicipalityServiceDep = Annotated[
  MunicipalityService, Depends(get_municipality_service)
]
MunicipalityId = Annotated[str, Path(pattern=r"^\d{5}$")]
