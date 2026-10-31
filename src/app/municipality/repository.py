from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, defer

from src.app.municipality.models import Municipality
from src.app.municipality.schemas import MunicipalityFilters


class MunicipalityRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def _apply_filters(self, query: Select, filters: MunicipalityFilters) -> Select:
    if filters.search:
      query = query.where(
        func.unaccent(Municipality.name).ilike(func.unaccent(f"%{filters.search}%"))
      )
    if filters.state_id:
      query = query.where(Municipality.state_id == filters.state_id)
    return query

  def list(
    self,
    filters: MunicipalityFilters | None,
    skip: int | None,
    limit: int | None,
  ) -> list[Municipality]:
    query = (
      select(Municipality)
      .options(defer(Municipality.geometry, raiseload=True))
      .order_by(Municipality.id)
    )

    if filters:
      query = self._apply_filters(query, filters)
    if skip is not None:
      query = query.offset(skip)
    if limit is not None:
      query = query.limit(limit)

    return list(self.db.scalars(query).all())

  def count(self, filters: MunicipalityFilters | None) -> int:
    query = select(func.count(Municipality.id))
    if filters:
      query = self._apply_filters(query, filters)
    return self.db.scalar(query) or 0

  def get_by_id(self, municipality_id: str) -> Municipality | None:
    query = (
      select(Municipality)
      .options(defer(Municipality.geometry, raiseload=True))
      .where(Municipality.id == municipality_id)
    )
    return self.db.scalars(query).one_or_none()
