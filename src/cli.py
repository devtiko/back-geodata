from collections.abc import Callable

import typer
from sqlalchemy.orm import Session

from src.database.seeds.states import seed_states
from src.database.session import session_local

app = typer.Typer(help="Comandos de mantenimiento para GeoData API.")


def run_db_command[T](func: Callable[[Session], T]) -> T:
  with session_local.begin() as session:
    return func(session)


@app.command()
def states() -> None:
  count = run_db_command(seed_states)
  typer.echo(f"Se cargaron {count} estados")


if __name__ == "__main__":
  app()
