from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, defer

from src.app.locality.models import Locality
from src.app.locality.schemas import LocalityFilters


class LocalityRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def _apply_filters(self, query: Select, filters: LocalityFilters) -> Select:
    if filters.search:
      query = query.where(Locality.name.ilike(f"%{filters.search}%"))
    if filters.state_id:
      query = query.where(Locality.state_id == filters.state_id)
    if filters.municipality_id:
      query = query.where(Locality.municipality_id == filters.municipality_id)
    return query

  def list(
    self, filters: LocalityFilters | None, skip: int | None, limit: int | None
  ) -> list[Locality]:
    query = (
      select(Locality)
      .options(defer(Locality.geometry, raiseload=True))
      .order_by(Locality.id)
    )
    if filters:
      query = self._apply_filters(query, filters)
    if skip is not None:
      query = query.offset(skip)
    if limit is not None:
      query = query.limit(limit)
    return list(self.db.scalars(query).all())

  def count(self, filters: LocalityFilters | None) -> int:
    query = select(func.count(Locality.id))
    if filters:
      query = self._apply_filters(query, filters)
    return self.db.scalar(query) or 0

  def get_by_id(self, locality_id: str) -> Locality | None:
    query = (
      select(Locality)
      .options(defer(Locality.geometry, raiseload=True))
      .where(Locality.id == locality_id)
    )
    return self.db.scalars(query).one_or_none()
