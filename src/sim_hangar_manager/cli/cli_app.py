from pathlib import Path
from typing import Annotated

import typer

from sim_hangar_manager.version import APP_VERSION

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

app = typer.Typer(
    name="simhm",
    help="Sim Hangar Manager - Manage your personal Flight Simulator Hangar.",
    context_settings=CONTEXT_SETTINGS,
    add_completion=False,
    no_args_is_help=True
)

add_app = typer.Typer(help="Adds Aircraft model or an Aircraft to the database")
list_app = typer.Typer(help="List Aircraft models or Aircraft registered in the database")
edit_app = typer.Typer(help="Edits Aircraft model or Aircraft.")
delete_app = typer.Typer(help="Deletes an Aircraft model or Aircraft.")
show_app = typer.Typer(help="Shows an Aircraft model or Aircraft.")

app.add_typer(add_app, name="add")
app.add_typer(list_app, name="list")
app.add_typer(edit_app, name="edit")
app.add_typer(delete_app, name="delete")
app.add_typer(show_app, name="show")


@app.command()
def cli():
    """
    Launch interactive Command Line Interface tool
    """
    from sim_hangar_manager.main import bootstrap_application
    
    interactive_cli = bootstrap_application()
    interactive_cli.run()


@add_app.command("model")
def add_model():
    """Registers a new Aircraft Model in the database"""
    from sim_hangar_manager.main import bootstrap_add_aircraft_model_view
    add_model_view = bootstrap_add_aircraft_model_view()
    add_model_view.run()


@list_app.command("models")
def list_models():
    """List Aircraft Models in the database"""
    from sim_hangar_manager.main import bootstrap_list_aircraft_model_view
    list_aircraft_model_view = bootstrap_list_aircraft_model_view()
    list_aircraft_model_view.list_aircraft_models()


@add_app.command("aircraft")
def add_aircraft():
    """Registers a new Aircraft in the database"""

@app.command()
def scan(path: Annotated[Path, typer.Option("--path","-p", help="Path to scan")] = None,
         confirm: Annotated[bool, typer.Option("--confirm","-c", help="Confirm Modules to be imported. " \
         "This flag only works when Path is provided, default is False")] = False,
         skip_validation: Annotated[bool, typer.Option("--skip-validation","-s", help="Skip Standard Package validation, this is for packages that do not follow standard structure. This flag only works when Path is provided, default is False")] = False,
         overwrite: Annotated[bool, typer.Option("--overwrite","-o", help="Overwrites some parameters of existing aircraft addons already registered in the database. This flag only works when Path is provided, default is False")] = False,
         dry_run: Annotated[bool, typer.Option("--dry-run","-d", help="Scan for modules but will not save data to the database. This flag only works when Path is provided, default is False")] = False,
         log: Annotated[Path, typer.Option("--log","-l", help="Define an output file to write scan operation log. " \
         "This flag only works when Path is provided")] = None,
         ):
    """
    Scans the directory looking for Modules to be added to the database.
    """

    from sim_hangar_manager.main import bootstrap_scan_context

    scan_view, log_file_handle = bootstrap_scan_context(log_path=log)

    try:
        if path:
            scan_view.scan_modules_cli(scan_directory=path, 
                                       ask_confirmation=confirm, 
                                       skip_validation=skip_validation, 
                                       overwrite_aircraft_module=overwrite,
                                       dry_run=dry_run)
        else:
            scan_view.scan_modules()

    finally:
        if log_file_handle:
            log_file_handle.close()
    
    
@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Shows App version.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,):
    pass


def version_callback(value: bool):
    """Shows App Version"""
    if value:
        typer.echo(f"Sim Hangar Manager - version {APP_VERSION}")
        raise typer.Exit()


if __name__ == "__main__":
    app()