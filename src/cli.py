from collections.abc import Callable

import typer
from rich.console import Console
from sqlalchemy.orm import Session

from src.database.seeds.localities import seed_localities
from src.database.seeds.municipalities import seed_municipalities
from src.database.seeds.states import seed_states
from src.database.session import session_local

app = typer.Typer(help="Comandos de mantenimiento para GeoData API.")
console = Console()


def run_db_command[T](func: Callable[[Session], T]) -> T:
  with session_local.begin() as session:
    return func(session)


@app.command()
def states() -> None:
  with console.status("Cargando estados...", spinner="dots"):
    count = run_db_command(seed_states)
  typer.echo(f"Se cargaron {count} estados")


@app.command()
def municipalities() -> None:
  with console.status("Cargando municipios...", spinner="dots"):
    count = run_db_command(seed_municipalities)
  typer.echo(f"Se cargaron {count} municipios")


@app.command()
def localities() -> None:
  with console.status("Cargando localidades...", spinner="dots"):
    count = run_db_command(seed_localities)
  typer.echo(f"Se cargaron {count} localidades")


if __name__ == "__main__":
  app()
