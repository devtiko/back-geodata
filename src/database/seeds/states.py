import json
from pathlib import Path
from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.app.state.models import State

STATES_FILE = Path(__file__).resolve().parents[3] / "data" / "states.json"


def _parse_srid(geometry: dict[str, Any], state_id: Any) -> int:
  try:
    return int(geometry["crs"])
  except (KeyError, TypeError, ValueError) as error:
    raise ValueError(f"Missing or invalid geometry CRS for state {state_id}") from error


def _state_values(record: dict[str, Any]) -> dict[str, Any]:
  geometry = record.get("geometry")
  geometry_expression = None

  if geometry is not None:
    srid = _parse_srid(geometry, record.get("cvegeo"))

    geojson_geometry = {
      "type": geometry["type"],
      "coordinates": geometry["coordinates"],
    }

    geometry_expression = func.ST_SetSRID(
      func.ST_GeomFromGeoJSON(json.dumps(geojson_geometry)), srid
    )

  return {
    "id": record["cvegeo"],
    "name": record["nomgeo"],
    "short_name": record.get("nom_abrev"),
    "geometry": geometry_expression,
  }


def seed_states(db: Session, source: Path = STATES_FILE) -> int:
  with source.open(encoding="utf-8") as states_file:
    records = json.load(states_file)

  if not isinstance(records, list):
    raise TypeError(f"Expected a JSON array in {source}")

  values = [_state_values(record) for record in records]
  if not values:
    return 0

  statement = insert(State).values(values)
  statement = statement.on_conflict_do_update(
    index_elements=[State.id],
    set_={
      "name": statement.excluded.name,
      "short_name": statement.excluded.short_name,
      "geometry": statement.excluded.geometry,
    },
  )
  db.execute(statement)
  return len(values)
