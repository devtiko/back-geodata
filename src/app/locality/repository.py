from __future__ import annotations

from typing import NamedTuple

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, defer

from src.app.locality.models import Locality
from src.app.locality.schemas import LocalityFilters, NearbyFilters


class NearbyLocalityRow(NamedTuple):
  locality: Locality
  distance_km: float


class LocalityRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def _apply_filters(self, query: Select, filters: LocalityFilters) -> Select:
    if filters.search:
      query = query.where(
        func.unaccent(Locality.name).ilike(func.unaccent(f"%{filters.search}%"))
      )
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

  def nearby(
    self,
    filters: NearbyFilters,
    skip: int | None,
    limit: int | None,
  ) -> tuple[list[NearbyLocalityRow], int]:
    query_point = func.ST_SetSRID(
      func.ST_MakePoint(filters.longitude, filters.latitude), 4326
    )
    locality_point = func.ST_SetSRID(
      func.ST_MakePoint(Locality.longitude, Locality.latitude), 4326
    )
    distance_meters = func.ST_DistanceSphere(locality_point, query_point)
    query: Select = (
      select(Locality, (distance_meters / 1000).label("distance_km"))
      .where(Locality.latitude.is_not(None), Locality.longitude.is_not(None))
      .where(distance_meters <= filters.radius_km * 1000)
      .options(defer(Locality.geometry, raiseload=True))
    )

    total = self.db.scalar(select(func.count()).select_from(query.subquery())) or 0
    results_query = query.order_by(distance_meters, Locality.id)

    if skip is not None:
      results_query = results_query.offset(skip)
    if limit is not None:
      results_query = results_query.limit(limit)

    rows = self.db.execute(results_query).unique().all()
    return [NearbyLocalityRow(row[0], float(row[1])) for row in rows], total
