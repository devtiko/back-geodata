from typing import NamedTuple

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from src.app.locality.models import Locality
from src.app.municipality.models import Municipality
from src.app.state.models import State


class ReverseMatch(NamedTuple):
  locality: Locality | None
  municipality: Municipality | None
  state: State | None


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
