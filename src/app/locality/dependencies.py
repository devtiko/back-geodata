from typing import Annotated

from fastapi import Depends, Path

from src.app.locality.repository import LocalityRepository
from src.app.locality.service import LocalityService
from src.database.session import DbSession


def get_locality_service(db: DbSession) -> LocalityService:
  return LocalityService(LocalityRepository(db))


LocalityServiceDep = Annotated[LocalityService, Depends(get_locality_service)]
LocalityId = Annotated[str, Path(pattern=r"^\d{9}$")]
