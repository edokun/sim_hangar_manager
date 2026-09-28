import sys

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.utils import get_style
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from sim_hangar_manager.cli.forms.create_aircraft_model_form import \
    prompt_add_aircraft_model
from sim_hangar_manager.cli.views.aircraft_model_detail_view import \
    AircraftModelDetailView
from sim_hangar_manager.cli.views.list_aircraft_models_view import \
    display_aircraft_models_table
from sim_hangar_manager.cli.views.scan_view import ScanAndImportView
from sim_hangar_manager.cli.views.search_view import SearchAircraftView
from sim_hangar_manager.database.connection import SessionLocal
from sim_hangar_manager.database.repository.aircraft_model_repository import \
    AircraftModelRepository
from sim_hangar_manager.service.aircraft_model_service import \
    AircraftModelService
from sim_hangar_manager.service.scanner_service import HangarScannerService

console = Console()


def get_service(db_session) -> AircraftModelService:
    """
    Helper function to wire up the dependency chain for a given DB session.
    """
    repository = AircraftModelRepository(db_session)
    return AircraftModelService(repository)


def handle_create_model():
    """
    Flow for collecting raw data and inserting a new aircraft module.
    """
    raw_data = prompt_add_aircraft_model()
    if not raw_data:
        return

    db = SessionLocal()
    try:
        service = get_service(db)
        saved_model = service.register_new_module(raw_data)
        console.print(
            f"\n[bold green]✔ Successfully registered '{saved_model.name}' (ID: {saved_model.id})[/bold green]\n"
        )
    except Exception as e:
        console.print(f"\n[bold red]✖ Failed to save record: {e}[/bold red]\n")
    finally:
        db.close()


def handle_list_models():
    """
    Flow for fetching and displaying registered aircraft modules.
    """
    db = SessionLocal()
    try:
        service = get_service(db)
        models = service.get_all_aircraft_models()
        display_aircraft_models_table(models)
    except Exception as e:
        console.print(f"\n[bold red]✖ Error reading Aircraft modules: {e}[/bold red]\n")
    finally:
        db.close()


def handle_module_scan_option():
    db = SessionLocal()
    try:
        aircraft_model_service = get_service(db)
        scanner_service = HangarScannerService()
        view = ScanAndImportView(scanner_service, aircraft_model_service)
        view.run()
    except Exception as e:
            print(f"\n[ERROR] Failed to scan modules: {e}\n")
    finally:
        db.close()

def handle_module_search_option():
    db = SessionLocal()
    try:
        service = get_service(db)
        search_view = SearchAircraftView(service)
        selected = search_view.run()
        if selected:
            detail_view = AircraftModelDetailView(service)
            detail_view.run(selected)

    except Exception as e:
            print(f"\n[ERROR] Failed to scan modules: {e}\n")
    finally:
        db.close()

   
def main_menu():
    """
    Main interactive loop for the CLI application.
    """
    while True:
        console.clear()

        title = Text("SIM HANGAR MANAGER - CLI", style="bold white", justify="center")
        version = Text("v0.1.0", style="dim white", justify="right")
        instructions = Text.from_markup("[bold cyan]Use the arrows [yellow](↑/↓)[/yellow] and press [yellow]Enter[/yellow] to select:[/bold cyan]", justify="left")

        instructions_panel_content = Columns([instructions, version], expand=True)

        header_panel = Panel(
            title, 
            box = box.DOUBLE, 
            border_style="bold white", 
            style="on blue",
            padding=(1, 2)
        )

        console.print(header_panel)

        console.print(Panel(instructions_panel_content, border_style="blue"))

        try:
            custom_style = get_style({
                "questionmark": "#000000",
                "pointer": "#00aaff bold",
                "highlighted": "#ffffff bold",
                "selected": "#00ff00",
                "separator": "#cc5500",
                "instruction": "#888888",
            }, style_override=True)

            choice = inquirer.select(
                message="",
                qmark="",
                amark="",
                choices=[
                    Choice(value="1", name="1. ➕ Add New Aircraft Module"),
                    Choice(value="2", name="2. 🔍 Scan folder for Aircraft Modules"),
                    Choice(value="3", name="3. 📋 List All Aircraft Modules"),
                    Choice(value="4", name="4. 🔎 Search/Filter Aircraft Modules"),
                    Choice(value=None, name="5. 🚪 Exit"),
                ],
                pointer="❯ ",
                style=custom_style,
            ).execute()

            if not choice:
                console.clear()
                console.print("\n[bold blue]Closing SIM HANGAR MANAGER... Bye![/bold blue]\n")
                sys.exit(0)

            if choice.startswith("1"):
                handle_create_model()
            elif choice.startswith("2"):
                handle_module_scan_option()
            elif choice.startswith("3"):
                handle_list_models()
            elif choice.startswith("4"):
                handle_module_search_option()

        except KeyboardInterrupt:
            console.print("\n[bold blue]Closing SIM HANGAR MANAGER... Bye![/bold blue]\n")
            sys.exit(0)
