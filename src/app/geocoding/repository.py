from typing import Literal, NamedTuple

from sqlalchemy import Select, case, func, literal, select, union_all
from sqlalchemy.orm import Session, joinedload

from src.app.geocoding.schemas import GeocodingFilters
from src.app.locality.models import Locality
from src.app.municipality.models import Municipality
from src.app.state.models import State


class ReverseMatch(NamedTuple):
  locality: Locality | None
  municipality: Municipality | None
  state: State | None


class SearchRow(NamedTuple):
  type: Literal["locality", "municipality", "state"]
  id: str
  name: str
  short_name: str | None
  latitude: float | None
  longitude: float | None


class GeocodingRepository:
  def __init__(self, db: Session) -> None:
    self.db = db

  def reverse(self, latitude: float, longitude: float) -> ReverseMatch:
    point = func.ST_Transform(
      func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326), 6365
    )
    locality = self._find_locality(point)

    if locality is None:
      locality = self._find_nearest_locality(latitude, longitude)

    if locality is not None:
      return ReverseMatch(
        locality=locality,
        municipality=locality.municipality,
        state=locality.municipality.state,
      )

    municipality = self._find_municipality(point)
    if municipality is not None:
      return ReverseMatch(
        locality=None,
        municipality=municipality,
        state=municipality.state,
      )

    state = self._find_state(point)
    return ReverseMatch(
      locality=None,
      municipality=None,
      state=state,
    )

  def search(
    self,
    filters: GeocodingFilters,
    skip: int | None,
    limit: int | None,
  ) -> tuple[list[SearchRow], int]:
    locality_query = self._locality_search_query(filters)
    municipality_query = self._municipality_search_query(filters)
    state_query = self._state_search_query(filters)

    combined = union_all(locality_query, municipality_query, state_query).subquery()

    total = self.db.scalar(select(func.count()).select_from(combined)) or 0
    query = select(combined).order_by(
      combined.c.rank, combined.c.type_order, combined.c.id
    )

    if skip is not None:
      query = query.offset(skip)
    if limit is not None:
      query = query.limit(limit)

    rows = self.db.execute(query).all()

    items = [
      SearchRow(
        type=row[0],
        id=row[1],
        name=row[2],
        short_name=row[3],
        latitude=row[4],
        longitude=row[5],
      )
      for row in rows
    ]

    return items, total

  @staticmethod
  def _rank_for(model, search_text: str):
    normalized_query = func.unaccent(func.lower(search_text))
    normalized_name = func.unaccent(func.lower(model.name))
    return case(
      (normalized_name == normalized_query, 0),
      (normalized_name.like(func.unaccent(func.lower(f"{search_text}%"))), 1),
      else_=2,
    )

  def _entity_search_query(
    self,
    model,
    entity_type: str,
    type_order: int,
    filters: GeocodingFilters,
    short_name=None,
    latitude=None,
    longitude=None,
  ) -> Select:
    query = select(
      literal(entity_type).label("type"),
      model.id.label("id"),
      model.name.label("name"),
      (short_name if short_name is not None else literal(None)).label("short_name"),
      (latitude if latitude is not None else literal(None)).label("latitude"),
      (longitude if longitude is not None else literal(None)).label("longitude"),
      self._rank_for(model, filters.query).label("rank"),
      literal(type_order).label("type_order"),
    ).where(func.unaccent(model.name).ilike(func.unaccent(f"%{filters.query}%")))
    return query

  def _locality_search_query(self, filters: GeocodingFilters) -> Select:
    query = self._entity_search_query(
      model=Locality,
      entity_type="locality",
      type_order=0,
      filters=filters,
      latitude=Locality.latitude,
      longitude=Locality.longitude,
    )
    if filters.state_id:
      query = query.where(Locality.state_id == filters.state_id)
    if filters.municipality_id:
      query = query.where(Locality.municipality_id == filters.municipality_id)
    return query

  def _municipality_search_query(self, filters: GeocodingFilters) -> Select:
    query = self._entity_search_query(
      model=Municipality,
      entity_type="municipality",
      type_order=1,
      filters=filters,
    )
    if filters.state_id:
      query = query.where(Municipality.state_id == filters.state_id)
    if filters.municipality_id:
      query = query.where(Municipality.id == filters.municipality_id)
    return query

  def _state_search_query(self, filters: GeocodingFilters) -> Select:
    query = self._entity_search_query(
      model=State,
      entity_type="state",
      type_order=2,
      filters=filters,
      short_name=State.short_name,
    )
    if filters.state_id:
      query = query.where(State.id == filters.state_id)
    return query

  def _find_locality(self, point) -> Locality | None:
    query: Select = (
      select(Locality)
      .options(joinedload(Locality.municipality).joinedload(Municipality.state))
      .where(Locality.geometry.is_not(None))
      .where(func.ST_Covers(Locality.geometry, point))
      .order_by(Locality.id)
      .limit(1)
    )
    return self.db.scalars(query).one_or_none()

  def _find_municipality(self, point) -> Municipality | None:
    query: Select = (
      select(Municipality)
      .options(joinedload(Municipality.state))
      .where(Municipality.geometry.is_not(None))
      .where(func.ST_Covers(Municipality.geometry, point))
      .order_by(Municipality.id)
      .limit(1)
    )
    return self.db.scalars(query).one_or_none()

  def _find_state(self, point) -> State | None:
    query: Select = (
      select(State)
      .where(State.geometry.is_not(None))
      .where(func.ST_Covers(State.geometry, point))
      .order_by(State.id)
      .limit(1)
    )
    return self.db.scalars(query).one_or_none()

  def _find_nearest_locality(
    self, latitude: float, longitude: float
  ) -> Locality | None:
    max_distance_meters = 5_000
    query_point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
    locality_point = func.ST_SetSRID(
      func.ST_MakePoint(Locality.longitude, Locality.latitude), 4326
    )
    distance = func.ST_DistanceSphere(locality_point, query_point)
    query: Select = (
      select(Locality)
      .options(joinedload(Locality.municipality).joinedload(Municipality.state))
      .where(Locality.latitude.is_not(None), Locality.longitude.is_not(None))
      .where(distance <= max_distance_meters)
      .order_by(distance, Locality.id)
      .limit(1)
    )
    return self.db.scalars(query).one_or_none()
