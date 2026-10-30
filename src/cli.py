from collections.abc import Callable

import typer
from rich.console import Console
from sqlalchemy.orm import Session

from src.database.seeds.localities import seed_localities
from src.database.seeds.municipalities import seed_municipalities
from src.database.seeds.states import seed_states
from src.database.session import session_local

app = typer.Typer(
  help="Comandos de mantenimiento para GeoData API.", invoke_without_command=True
)
console = Console()


def run_db_command[T](func: Callable[[Session], T]) -> T:
  with session_local.begin() as session:
    return func(session)


@app.callback()
def main(ctx: typer.Context) -> None:
  if ctx.invoked_subcommand is not None:
    return

  with session_local.begin() as session:
    with console.status("Cargando estados...", spinner="dots"):
      states_count = seed_states(session)
    with console.status("Cargando municipios...", spinner="dots"):
      municipalities_count = seed_municipalities(session)
    with console.status("Cargando localidades...", spinner="dots"):
      localities_count = seed_localities(session)

  typer.echo(f"Se cargaron {states_count} estados")
  typer.echo(f"Se cargaron {municipalities_count} municipios")
  typer.echo(f"Se cargaron {localities_count} localidades")


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
