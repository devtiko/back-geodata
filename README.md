# back-geodata

API para consultar datos geográficos de estados, municipios y localidades, con búsqueda y geocodificación inversa. Está construida con FastAPI, SQLAlchemy y PostgreSQL/PostGIS.

## Requisitos

- Python 3.12 o superior y [`uv`](https://docs.astral.sh/uv/).
- Docker Compose para ejecutar PostgreSQL con PostGIS localmente.

## Configuración y arranque

1. Usa [`.env.template`](.env.template) como referencia para crear y configurar tu `.env` local.
2. Instala las dependencias bloqueadas:

   ```bash
   uv sync
   ```

3. Inicia la base de datos y aplica las migraciones:

   ```bash
   docker compose up -d postgres
   uv run alembic upgrade head
   ```

4. Carga los datos geográficos y arranca la API:

   ```bash
   uv run python -m src.cli
   uv run uvicorn src.main:app --reload
   ```

La carga completa ejecuta los seeds en este orden: estados, municipios y localidades. Los comandos `uv run python -m src.cli states`, `municipalities` y `localities` permiten ejecutar una carga individual.

## API

Los endpoints están bajo `/api/v1`:

- `/states` — consulta estados.
- `/municipalities` — consulta municipios.
- `/localities` — consulta localidades.
- `/geocoding` — búsqueda geográfica.

Con el servidor en marcha, la documentación interactiva de FastAPI está disponible en `/docs` y el esquema OpenAPI en `/openapi.json`.

## Desarrollo

- Las migraciones de esquema se mantienen en `alembic/versions/`; aplica cambios locales con `uv run alembic upgrade head`.
- Los datos geográficos de localidades provienen de [geo-data](docs/geo-data.md) y se cargan mediante el CLI de mantenimiento.

### Pruebas

Las pruebas unitarias no necesitan servicios externos. Las pruebas de integración levantan un contenedor temporal con PostgreSQL/PostGIS mediante Testcontainers, aplican las migraciones y eliminan el contenedor al finalizar. Para ejecutarlas, Docker debe estar instalado y en ejecución.

```bash
uv run pytest tests/unit
uv run pytest tests/integration
uv run pytest
```
