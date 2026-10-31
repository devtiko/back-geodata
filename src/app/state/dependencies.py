from typing import Annotated

from fastapi import Depends, Path

from src.app.state.repository import StateRepository
from src.app.state.service import StateService
from src.database.session import DbSession


def get_state_service(
  db: DbSession,
) -> StateService:
  return StateService(StateRepository(db))


StateServiceDep = Annotated[StateService, Depends(get_state_service)]
StateId = Annotated[str, Path(pattern=r"^\d{2}$")]
