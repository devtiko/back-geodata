from sqlalchemy import Column, DateTime, Integer, MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func

POSTGRES_INDEXES_NAMING_CONVENTION = {
  "ix": "%(column_0_label)s_idx",
  "uq": "%(table_name)s_%(column_0_name)s_key",
  "ck": "%(table_name)s_%(constraint_name)s_check",
  "fk": "%(table_name)s_%(column_0_name)s_fkey",
  "pk": "%(table_name)s_pkey",
}

metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)


class Base(DeclarativeBase):
  metadata = metadata

  id = Column(Integer, primary_key=True)
  created_at = Column(
    DateTime(timezone=True),
    nullable=False,
    default=func.now(),
    server_default=func.now(),
  )
  updated_at = Column(
    DateTime(timezone=True),
    nullable=False,
    default=func.now(),
    server_default=func.now(),
    onupdate=func.now(),
  )
