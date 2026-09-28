from typing import Optional

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from rich.console import Console

#from sim_hangar_manager.cli.views.aircraft_model_detail_view import AircraftModelDetailView
from sim_hangar_manager.database.models import AircraftModel
from sim_hangar_manager.service.aircraft_model_service import \
    AircraftModelService

#from rich.panel import Panel
#from rich.table import Table


console = Console()


class SearchAircraftView:

    def __init__(self, aircraft_model_service: AircraftModelService):
        self.aircraft_model_service = aircraft_model_service

    def run(self) -> Optional[AircraftModel]:
        console.clear()
        console.rule("[bold cyan]Search and Filter Modules/Addons[/bold cyan]\n")

        aircraft_modules = self.aircraft_model_service.get_all_aircraft_models()

        if not aircraft_modules:
            console.print("[yellow]No Modules Addons registered.[/yellow]\n")
            inquirer.text(message="Press Enter to go back...").execute()
            return None

        # Prepare Options to be visible for search
        choices = [
            Choice(
                value=ac,
                name=f"{ac.name} | ICAO: {ac.icao_code or 'N/A'} | Dev: {ac.developer} | Sim: {ac.simulator}",
            )
            for ac in aircraft_modules
        ]

        # InquirerPy Fuzzy for real time dynamic search
        selected_aircraft: AircraftModel = inquirer.fuzzy(
            message="Type to filter (Name, ICAO, Developer, Simulator):",
            choices=choices,
            match_exact=False,
            transformer=lambda result: f"Selected: {result}" if result else "",
        ).execute()

        #if selected_aircraft:
        #    detail_view = AircraftModelDetailView(self.aircraft_model_service)
        #    detail_view.show(selected_aircraft)

        return selected_aircraft

    '''
    def _display_aircraft_card(self, aircraft: AircraftModel):
        # refactor this, use aircraft_model_detail_view
        """Show a detailed table with selected module."""
        console.clear()
        console.rule(f"[bold green]Module details: {aircraft.name}[/bold green]\n")

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="white")

        table.add_row("ID:", str(aircraft.id))
        table.add_row("Name:", aircraft.name)
        table.add_row("module name:", aircraft.module_name)
        table.add_row("Developer:", aircraft.developer)
        table.add_row("ICAO code:", aircraft.icao_code or "[dim]Sin asignar[/dim]")
        table.add_row("Simulator:", aircraft.simulator)
        table.add_row("Version:", aircraft.version or "1.0.0")
        table.add_row("Location:", aircraft.module_file_location_1 or "N/A")
        table.add_row("Notes:", aircraft.notes or "[dim]N/A[/dim]")

        console.print(Panel(table, expand=False, title="[bold]Module data[/bold]"))
        console.print()
    '''

    '''
    def handle_selection_menu(self, aircraft: AircraftModel):
        # Refactor this might not be needed
        """Menú de acciones contextuales sobre el módulo seleccionado."""
        while True:
            # self._display_aircraft_card(aircraft)

            action = inquirer.select(
                message=f"Options for '{aircraft.name}':",
                choices=[
                    {"name": "1. See full details", "value": "view_details"},
                    {"name": "2. Edit", "value": "edit"},
                    {"name": "3. Go Back to Search view", "value": "search_again"},
                    {"name": "4. Back to Main Menu", "value": "back"},
                ],
            ).execute()

            if action == "view_details":
                detail_view = AircraftDetailView(self.aircraft_model_service)
                detail_view.show(aircraft)

            elif action == "edit":
                self._edit_aircraft(aircraft)

            elif action == "search_again":
                new_selection = self.run()
                if new_selection:
                    aircraft = new_selection
                else:
                    break  # Si no selecciona nada en la nueva búsqueda, sale al menú

            elif action == "back":
                break  # Sale del bucle y regresa al menú principal


    def _edit_aircraft(self, aircraft: AircraftModel):
        # Refactor this, maybe not needed
        console.print("\n[bold yellow]--- Edición de Módulo ---[/bold yellow]")

        new_icao = inquirer.text(
            message="Nuevo Código ICAO:",
            default=aircraft.icao_code or "",
        ).execute()

        new_notes = inquirer.text(
            message="Nuevas Notas:",
            default=aircraft.notes or "",
        ).execute()

        # Actualización en la base de datos a través del servicio
        self.aircraft_model_service.update_aircraft_model(
            aircraft.id,
            icao_code=new_icao.strip().upper(),
            notes=new_notes.strip(),
        )
        
        # Refrescar el objeto local
        aircraft.icao_code = new_icao.strip().upper()
        aircraft.notes = new_notes.strip()
        
        console.print("[bold green]¡Módulo actualizado correctamente![/bold green]")
        inquirer.text(message="Presiona Enter para continuar...").execute()
    '''