# Repository guide

- This is a single Python 3.12+ project managed with `uv` (`pyproject.toml` and `uv.lock`); run commands through `uv run` so the locked environment is used.
- API entrypoint is `src.main:app` (`uv run uvicorn src.main:app --reload`); app routers for states, municipalities, localities, and geocoding are mounted under `/api/v1`.
- `src/cli.py` is the Typer maintenance CLI. Running it without a subcommand seeds states, municipalities, then localities; targeted commands are `uv run python -m src.cli states|municipalities|localities`.
- Database schema changes belong in Alembic revisions under `alembic/versions`; configuration is in `alembic.ini` and connection setup in `alembic/env.py`. Apply migrations with `uv run alembic upgrade head`.
- Local PostgreSQL/PostGIS is defined in `docker-compose.yml`; its port and credentials come from `.env` (`DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`). Database-backed CLI, migrations, and API operations require it running.
- Geographic source data is stored under `data/localities/` as JSON; locality seeding consumes this data, so preserve its filenames and structure when changing seed logic or fixtures.
- No test, lint, formatter, or typecheck command is configured in `pyproject.toml`; verify focused changes with available project commands rather than assuming a test suite exists.
