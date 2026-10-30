from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class State(Base):
  __tablename__ = "states"

  id: Mapped[str] = mapped_column(String(2), primary_key=True)
  name: Mapped[str] = mapped_column(String, nullable=False)
  short_name: Mapped[str | None] = mapped_column(String, nullable=True)
  geometry: Mapped[WKBElement | None] = mapped_column(
    Geometry(geometry_type="MULTIPOLYGON", srid=6365), nullable=True
  )
