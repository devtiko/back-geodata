from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, defer

from src.app.state.models import State
from src.app.state.schemas import StateFilters


class StateRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def _apply_filters(self, query: Select, filters: StateFilters) -> Select:
    if filters is not None and filters.search:
      query = query.where(State.name.ilike(f"%{filters.search}%"))
    return query

  def list(
    self, filters: StateFilters | None, skip: int | None, limit: int | None
  ) -> list[State]:
    query = (
      select(State).options(defer(State.geometry, raiseload=True)).order_by(State.id)
    )

    if filters:
      query = self._apply_filters(query, filters)
    if skip is not None:
      query = query.offset(skip)
    if limit is not None:
      query = query.limit(limit)

    return list(self.db.scalars(query).all())

  def count(self, filters: StateFilters | None) -> int:
    query = select(func.count(State.id))
    if filters:
      query = self._apply_filters(query, filters)
    return self.db.scalar(query) or 0

  def get_by_id(self, state_id: str) -> State | None:
    query = (
      select(State)
      .options(defer(State.geometry, raiseload=True))
      .where(State.id == state_id)
    )
    return self.db.scalars(query).one_or_none()
