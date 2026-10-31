from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

from src.core.settings import settings

database_url = URL.create(
  drivername="postgresql+psycopg",
  username=settings.DB_USER,
  password=settings.DB_PASSWORD.get_secret_value(),
  host=settings.DB_HOST,
  port=settings.DB_PORT,
  database=settings.DB_NAME,
)

engine = create_engine(database_url)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
  db = session_local()
  try:
    yield db
  finally:
    db.close()


DbSession = Annotated[Session, Depends(get_db)]
