from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.state.models import State
from src.database.base import Base


class Municipality(Base):
  __tablename__ = "municipalities"

  id: Mapped[str] = mapped_column(String(5), primary_key=True)
  state_id: Mapped[str] = mapped_column(
    String(2), ForeignKey("states.id"), nullable=False, index=True
  )
  name: Mapped[str] = mapped_column(String, nullable=False)
  geometry: Mapped[WKBElement | None] = mapped_column(
    Geometry(geometry_type="MULTIPOLYGON", srid=6365), nullable=True
  )
  state: Mapped["State"] = relationship(back_populates="municipalities")
