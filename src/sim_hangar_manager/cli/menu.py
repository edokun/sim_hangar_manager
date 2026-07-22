from InquirerPy import inquirer
from rich.console import Console
import sys

from InquirerPy.base.control import Choice
from sim_hangar_manager.cli.views.aircraft_model_view import show_aircraft_model_details

from sim_hangar_manager.database.connection import SessionLocal
from sim_hangar_manager.database.repository.aircraft_model_repository import AircraftModelRepository
from sim_hangar_manager.service.aircraft_model_service import AircraftModelService

from sim_hangar_manager.cli.forms.create_aircraft_model_form import prompt_add_aircraft_model
from sim_hangar_manager.cli.views.list_aircraft_models_view import display_aircraft_models_table

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
        console.print(f"\n[bold green]✔ Successfully registered '{saved_model.name}' (ID: {saved_model.id})[/bold green]\n")
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
        console.print(f"\n[bold red]✖ Error reading hangar records: {e}[/bold red]\n")
    finally:
        db.close()

def handle_view_aircraft_model_details():
    """
    Select a Module and see all the details
    """
    db = SessionLocal()
    try:
        service = get_service(db)
        modules = service.get_all_aircraft_models()
        
        if not modules:
            print("\n[INFO] No aircraft modules found to display.\n")
            return

        # Creamos una lista de opciones. El usuario ve el nombre, pero la app obtiene el ID
        module_choices = [
            Choice(value=m.id, name=f"{m.name} ({m.developer})") for m in modules
        ]
        
        # Agregamos opción de cancelar
        module_choices.append(Choice(value=None, name="⬅️  Back to Main Menu"))

        selected_id = inquirer.select(
            message="Select an aircraft module to view details:",
            choices=module_choices
        ).execute()

        if selected_id is None:
            return

        # Asumiendo que tu servicio tiene un método get_by_id o similar
        selected_model = service.get_by_id(selected_id) 
        
        if selected_model:
            show_aircraft_model_details(selected_model)
            # Pausa para que el usuario pueda leer antes de regresar al menú
            input("Press Enter to return to the main menu...") 
            
    except Exception as e:
        print(f"\n[ERROR] Failed to load module details: {e}\n")
    finally:
        db.close()


def main_menu():
    """
    Main interactive loop for the CLI application.
    """
    while True:
        console.print("[bold cyan]=============================================[/bold cyan]")
        console.print("[bold white]        SIM HANGAR MANAGER - CLI              [/bold white]")
        console.print("[bold cyan]=============================================[/bold cyan]")

        try:
            choice = inquirer.select(
                message="Select an operational task:",
                choices=[
                    "1. Register New Aircraft Module",
                    "2. List All Hangar Modules",
                    "3. View Aircraft Module Details",
                    "4. Exit System"
                ]
            ).execute()

            if choice.startswith("1"):
                handle_create_model()
            elif choice.startswith("2"):
                handle_list_models()
            elif choice.startswith("3"):
                handle_view_aircraft_model_details()
            elif choice.startswith("4"):
                console.print("\n[bold blue]Closing Hangar Control... Have a great flight! ✈[/bold blue]\n")
                sys.exit(0)

        except KeyboardInterrupt:
            console.print("\n[bold blue]Closing Hangar Control... Have a great flight! ✈[/bold blue]\n")
            sys.exit(0)