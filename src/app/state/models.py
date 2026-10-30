from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
  from src.app.locality.models import Locality
  from src.app.municipality.models import Municipality


class State(Base):
  __tablename__ = "states"

  id: Mapped[str] = mapped_column(String(2), primary_key=True)
  name: Mapped[str] = mapped_column(String, nullable=False)
  short_name: Mapped[str | None] = mapped_column(String, nullable=True)
  geometry: Mapped[WKBElement | None] = mapped_column(
    Geometry(geometry_type="MULTIPOLYGON", srid=6365), nullable=True
  )
  municipalities: Mapped[list["Municipality"]] = relationship(back_populates="state")
  localities: Mapped[list["Locality"]] = relationship(back_populates="state")
