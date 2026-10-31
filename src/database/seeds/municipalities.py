import json
from pathlib import Path
from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.app.municipality.models import Municipality

BATCH_SIZE = 1_000
MUNICIPALITIES_DIR = Path(__file__).resolve().parents[3] / "data" / "municipalities"


def _parse_srid(geometry: dict[str, Any], municipality_id: Any) -> int:
  try:
    return int(geometry["crs"])
  except (KeyError, TypeError, ValueError) as error:
    raise ValueError(
      f"Missing or invalid geometry CRS for municipality {municipality_id}"
    ) from error


def _municipality_values(record: dict[str, Any]) -> dict[str, Any]:
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
    "state_id": record["cve_ent"],
    "geometry": geometry_expression,
  }


def _load_records(source: Path) -> list[dict[str, Any]]:
  sources = sorted(source.glob("*.json")) if source.is_dir() else [source]
  records: list[dict[str, Any]] = []

  for json_source in sources:
    with json_source.open(encoding="utf-8") as municipalities_file:
      file_records = json.load(municipalities_file)

    if not isinstance(file_records, list):
      raise TypeError(f"Expected a JSON array in {json_source}")

    records.extend(file_records)

  return records


def seed_municipalities(
  db: Session,
  source: Path = MUNICIPALITIES_DIR,
) -> int:
  records = _load_records(source)
  values = [_municipality_values(record) for record in records]
  if not values:
    return 0

  for start in range(0, len(values), BATCH_SIZE):
    batch = values[start : start + BATCH_SIZE]
    statement = insert(Municipality).values(batch)
    statement = statement.on_conflict_do_update(
      index_elements=[Municipality.id],
      set_={
        "name": statement.excluded.name,
        "state_id": statement.excluded.state_id,
        "geometry": statement.excluded.geometry,
      },
    )
    db.execute(statement)

  return len(values)
