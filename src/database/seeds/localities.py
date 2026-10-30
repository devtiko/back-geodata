import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.app.locality.models import Locality

BATCH_SIZE = 1_000
LOCALITIES_DIR = Path(__file__).resolve().parents[3] / "data" / "localities"


def _parse_srid(geometry: dict[str, Any], locality_id: Any) -> int:
  try:
    return int(geometry["crs"])
  except (KeyError, TypeError, ValueError) as error:
    raise ValueError(
      f"Missing or invalid geometry CRS for locality {locality_id}"
    ) from error


def _coordinate(record: dict[str, Any], field: str) -> Decimal | None:
  value = record.get(field)
  if value is None or value == "":
    return None
  try:
    return Decimal(str(value))
  except InvalidOperation as error:
    raise ValueError(f"Invalid {field} for locality {record.get('cvegeo')}") from error


def _locality_values(record: dict[str, Any]) -> dict[str, Any]:
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
    "municipality_id": f"{record['cve_ent']}{record['cve_mun']}",
    "latitud": _coordinate(record, "latitud"),
    "longitud": _coordinate(record, "longitud"),
    "geometry": geometry_expression,
  }


def _load_records(source: Path) -> list[dict[str, Any]]:
  sources = sorted(source.glob("*.json")) if source.is_dir() else [source]
  records: list[dict[str, Any]] = []
  for json_source in sources:
    with json_source.open(encoding="utf-8") as locality_file:
      file_records = json.load(locality_file)
    if not isinstance(file_records, list):
      raise TypeError(f"Expected a JSON array in {json_source}")
    records.extend(file_records)
  return records


def seed_localities(db: Session, source: Path = LOCALITIES_DIR) -> int:
  records = _load_records(source)
  values = [_locality_values(record) for record in records]
  for start in range(0, len(values), BATCH_SIZE):
    batch = values[start : start + BATCH_SIZE]
    statement = insert(Locality).values(batch)
    statement = statement.on_conflict_do_update(
      index_elements=[Locality.id],
      set_={
        "name": statement.excluded.name,
        "state_id": statement.excluded.state_id,
        "municipality_id": statement.excluded.municipality_id,
        "latitud": statement.excluded.latitud,
        "longitud": statement.excluded.longitud,
        "geometry": statement.excluded.geometry,
      },
    )
    db.execute(statement)
  return len(values)
