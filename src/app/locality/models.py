from typing import TYPE_CHECKING

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base

if TYPE_CHECKING:
  from src.app.municipality.models import Municipality
  from src.app.state.models import State


class Locality(Base):
  __tablename__ = "localities"

  id: Mapped[str] = mapped_column(String(9), primary_key=True)
  name: Mapped[str] = mapped_column(String, nullable=False)
  state_id: Mapped[str] = mapped_column(
    String(2), ForeignKey("states.id"), nullable=False, index=True
  )
  municipality_id: Mapped[str] = mapped_column(
    String(5), ForeignKey("municipalities.id"), nullable=False, index=True
  )
  latitud: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
  longitud: Mapped[float | None] = mapped_column(Numeric(11, 7), nullable=True)
  geometry: Mapped[WKBElement | None] = mapped_column(
    Geometry(geometry_type="MULTIPOLYGON", srid=6365), nullable=True
  )
  state: Mapped["State"] = relationship(back_populates="localities")
  municipality: Mapped["Municipality"] = relationship(back_populates="localities")
