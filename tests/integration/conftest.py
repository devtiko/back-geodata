import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, update
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.community.postgres import PostgresContainer

from src.app.locality.models import Locality
from src.app.municipality.models import Municipality
from src.app.state.models import State

ROOT = Path(__file__).resolve().parents[2]
POSTGIS_IMAGE = "postgis/postgis:17-master"
TEST_DB_NAME = "geodata_test"
TEST_DB_USER = "geodata_test"
TEST_DB_PASSWORD = "geodata_test"


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
  with PostgresContainer(
    image=POSTGIS_IMAGE,
    username=TEST_DB_USER,
    password=TEST_DB_PASSWORD,
    dbname=TEST_DB_NAME,
    driver="psycopg",
  ) as container:
    migration_env = os.environ.copy()
    migration_env.update(
      {
        "DB_HOST": container.get_container_host_ip(),
        "DB_PORT": str(container.get_exposed_port(5432)),
        "DB_USER": TEST_DB_USER,
        "DB_PASSWORD": TEST_DB_PASSWORD,
        "DB_NAME": TEST_DB_NAME,
      }
    )
    subprocess.run(
      [sys.executable, "-m", "alembic", "upgrade", "head"],
      cwd=ROOT,
      env=migration_env,
      check=True,
    )
    yield container


@pytest.fixture(scope="session")
def engine(postgres_container: PostgresContainer):
  test_engine = create_engine(postgres_container.get_connection_url())
  yield test_engine
  test_engine.dispose()


@pytest.fixture
def db_session(engine) -> Iterator[Session]:
  connection = engine.connect()
  transaction = connection.begin()
  session = sessionmaker(bind=connection)()
  try:
    yield session
  finally:
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def seed_geodata(db_session: Session) -> dict[str, str]:
  state = State(id="91", name="Córdoba", short_name="CB")
  municipality = Municipality(id="91001", state_id="91", name="San José")
  locality = Locality(
    id="910010001",
    name="Villa del Río",
    state_id="91",
    municipality_id="91001",
    latitude=4.6,
    longitude=-74.1,
  )
  nearby_locality = Locality(
    id="910010002",
    name="Villa Nueva",
    state_id="91",
    municipality_id="91001",
    latitude=4.605,
    longitude=-74.1,
  )
  distant_locality = Locality(
    id="910010003",
    name="Villa Lejana",
    state_id="91",
    municipality_id="91001",
    latitude=4.8,
    longitude=-74.1,
  )
  no_coordinates_locality = Locality(
    id="910010004",
    name="Villa Sin Coordenadas",
    state_id="91",
    municipality_id="91001",
    latitude=None,
    longitude=None,
  )
  db_session.add_all(
    [
      state,
      municipality,
      locality,
      nearby_locality,
      distant_locality,
      no_coordinates_locality,
    ]
  )
  db_session.flush()

  broad_polygon = "POLYGON((-74.3 4.4,-73.9 4.4,-73.9 4.8,-74.3 4.8,-74.3 4.4))"
  locality_polygon = (
    "POLYGON((-74.101 4.599,-74.099 4.599,-74.099 4.601,-74.101 4.601,-74.101 4.599))"
  )
  db_session.execute(
    update(State)
    .where(State.id == "91")
    .values(geometry=func.ST_Transform(func.ST_GeomFromText(broad_polygon, 4326), 6365))
  )
  db_session.execute(
    update(Municipality)
    .where(Municipality.id == "91001")
    .values(geometry=func.ST_Transform(func.ST_GeomFromText(broad_polygon, 4326), 6365))
  )
  db_session.execute(
    update(Locality)
    .where(Locality.id == "910010001")
    .values(
      geometry=func.ST_Transform(func.ST_GeomFromText(locality_polygon, 4326), 6365)
    )
  )
  db_session.flush()
  return {
    "state_id": state.id,
    "municipality_id": municipality.id,
    "locality_id": locality.id,
  }


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
  from src.database.session import get_db
  from src.main import app

  def override_get_db() -> Iterator[Session]:
    yield db_session

  app.dependency_overrides[get_db] = override_get_db
  try:
    with TestClient(app) as test_client:
      yield test_client
  finally:
    app.dependency_overrides.pop(get_db, None)
